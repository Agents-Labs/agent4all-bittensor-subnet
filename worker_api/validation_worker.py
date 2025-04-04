import gc
import time
import os
import multiprocessing
import logging
import traceback
import random
import shutil
from typing import List, Optional

import uvicorn
from tqdm.auto import tqdm
import pandas as pd
import torch
from fastapi import FastAPI, HTTPException, Header, Request, Response
from huggingface_hub.hf_api import HfApi, RepositoryNotFoundError, GatedRepoError
from dotenv import load_dotenv
from pydantic import BaseModel

from worker_api.evaluator import EvaluationScore, Evaluator, InferenceScore, RunError
from worker_api.persistence import SupabaseState
from common.scores import StatusEnum, Scores
from utilities.validation_utils import regenerate_hash
from utilities.repo_details import get_model_size, check_model_repo_details, ModelRepo
from utilities.event_logger import EventLogger
from scoring.common import EvaluateModelRequest

# Load environment variables
load_dotenv()

# Disable progress bars for Hugging Face Hub
from huggingface_hub.utils import disable_progress_bars
disable_progress_bars()

# Constants for model evaluation configuration
MAX_GENERATION_LEEWAY = 0.5
MAX_GENERATION_LENGTH = 200
LENGTH_DIFF_PENALTY_STEEPNESS = 2
MAX_AVG_LATENCY = 10000  # in milliseconds

MAX_MODEL_SIZE = 72 * 1024 * 1024 * 1024  # in bytes
MIN_REPO_SIZE = 40 * 1024 * 1024  # in bytes
MAX_REPO_SIZE = 80 * 1024 * 1024 * 1024  # in bytes
SAMPLE_SIZE = 1024  # number of samples for evaluation
BATCH_SIZE = 4  # batch size for evaluation
VOCAB_TRUNCATION = 1000  # truncate the vocab to top n tokens
PROB_TOP_K = 10  # correct token should be in the top n tokens
MAX_SEQ_LEN = 4096  # maximum sequence length for evaluation

SAVE_LEADERBOARD_EVERY = 60  # seconds
BLOCK_RATE_LIMIT = 28800  # every 14400 blocks = 48 hours

# Create FastAPI app instance
app = FastAPI()
supabaser = SupabaseState()
logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.ERROR)

# Initialize app.state variables
app.state.leaderboard_update_time = None
app.state.leaderboard = None
admin_key = os.environ["ADMIN_KEY"]
HF_TOKEN = os.environ.get("HF_ACCESS_TOKEN", "x")
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
hf_api = HfApi()

# Function to process model evaluations in a loop
def model_evaluation_queue(queue_id):
    try:
        while True:
            _model_evaluation_step(queue_id)
            time.sleep(5)  # Brief pause between evaluation attempts
    except Exception as e:
        app.state.event_logger.error("queue_error", queue_id=queue_id, error=e)

# Function to start multiple staggered evaluation queues
def start_staggered_queues(num_queues: int, stagger_seconds: int):
    processes: List[multiprocessing.Process] = []
    for i in range(num_queues):
        p = multiprocessing.Process(target=model_evaluation_queue, args=(i,))
        processes.append(p)
        p.start()
        logger.info(f"Started queue {i}")
        time.sleep(stagger_seconds + i)  # Stagger start times
    return processes

# Function that performs a single evaluation step for a model
def _model_evaluation_step(queue_id):
    time.sleep(random.random())  # Introduce randomness in timing

    request = get_next_model_to_eval()  # Get the next model to evaluate
    if request is None:  # Sentinel value to exit the process
        logger.info("No more models to evaluate. Sleep for 15 seconds before checking again.")
        return

    queued_message = f"model_eval_queue_start {request} {queue_id}"
    print(queued_message)
    app.state.event_logger.info(queued_message)

    try:
        result = _evaluate_model(request, queue_id)  # Evaluate the model
        if result is None:
            result = {"note": "incoherent model"}
        app.state.event_logger.info("model_eval_queue_complete", result=result, request=request)
    except Exception as e:
        logger.error(f"Error during model evaluation: {e}")
        app.state.event_logger.info("model_eval_queue_error", error=e)
    finally:
        gc.collect()  # Perform garbage collection

# Function to retrieve the next model for evaluation
def get_next_model_to_eval():
    response = supabaser.get_next_model_to_eval()
    if response is None:
        return None

    # Construct the evaluation request
    request = EvaluateModelRequest(
        repo_namespace=response["repo_namespace"],
        repo_name=response["repo_name"],
        chat_template_type=response["chat_template_type"],
        hash=response["hash"],
    )
    return request

# Mapping GPU IDs to string identifiers
GPU_ID_MAP = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
}

# Function that handles model evaluation
def _evaluate_model(request: EvaluateModelRequest, queue_id: int):
    """
    Evaluate a model based on its size and quality of outcomes.
    """
    supabaser.update_leaderboard_status(
        request.hash,
        StatusEnum.RUNNING,
        "Model evaluation in progress starting with inference score",
    )

    model_dir = f"/mnt/fast/tmp/{request.hash}"
    try:
        # Check disk space and trigger clean-up if over a threshold
        disk_stats = shutil.disk_usage("/mnt/fast/tmp")
        disk_percent_used = (disk_stats.used / disk_stats.total) * 100
        if disk_percent_used > 60:
            clean_old_folders()  # Clean old folders if space is low
        snapshot_download(repo_id=f"{request.repo_namespace}/{request.repo_name}", local_dir=model_dir, token=HF_TOKEN)
    except Exception as e:
        error_string = f"snapshot_download_error: could not download model from huggingface: {e}"
        supabaser.update_leaderboard_status(request.hash, StatusEnum.FAILED, error_string)
        raise RuntimeError(error_string)

    evaluator = Evaluator(gpu_ids=GPU_ID_MAP[queue_id], model_dir=model_dir, trace=False)
    try:
        inference_response = evaluator.inference_score(request)  # Run inference tests
        if isinstance(inference_response, RunError):
            raise Exception(inference_response.error)
        coherence_score = 1  # Placeholder for the coherence score
        judge_score = inference_response.judge_score  # Get the judge score

        # Log the results in the database
        upsert_row_supabase({
            "hash": request.hash,
            "judge_score": judge_score,
            "coherence_score": coherence_score,
            "notes": f"Inference score complete. Now computing evaluation score",
        })
    except Exception as e:
        error_string = f"inference_score_error with message: {e}"
        supabaser.update_leaderboard_status(request.hash, StatusEnum.FAILED, error_string)
        raise RuntimeError(error_string)

    # Evaluation result placeholders
    eval_score = 0
    latency_score = 0
    model_size_score = 0
    creativity_score = 0

    # Check for None values in scores
    if eval_score is None or latency_score is None or model_size_score is None or judge_score is None:
        raise HTTPException(status_code=500, detail="Error calculating scores, one or more scores are None")

    full_score_data = Scores()
    full_score_data.judge_score = judge_score

    try:
        upsert_row_supabase({
            "hash": request.hash,
            "total_score": full_score_data.judge_score,
            "status": StatusEnum.COMPLETED,
            "notes": f"scoring_status_complete",
        })
        logger.info(f"update_entry_complete now deleting directory {model_dir}")
    except Exception as e:
        failure_reason = str(e)
        logger.error(f"Updating leaderboard to FAILED: {failure_reason}")
        supabaser.update_leaderboard_status(request.hash, StatusEnum.FAILED, failure_reason)
        raise RuntimeError("Error updating leaderboard: " + failure_reason)
    
    # Attempt to clean up model directory
    try:
        shutil.rmtree(model_dir)
    except Exception as e:
        logger.error(f"could not delete {model_dir} because {e}")
    
    result = {
        "full_score_data": full_score_data,
    }
    return result

# Function to check if a repository exists on Hugging Face Hub
def repository_exists(repo_id):
    for attempt in range(3):
        try:
            hf_api.repo_info(repo_id)
            return True  # Repository exists
        except RepositoryNotFoundError:
            if attempt == 2:  # Last attempt
                return False  # Repo does not exist
        except GatedRepoError:
            if attempt == 2:  # Last attempt
                return False  # Repo is gated
        except Exception as e:
            app.state.event_logger.error("hf_repo_error", error=e)
            if attempt == 2:  # Last attempt
                return False  # Unrecoverable error

# Pydantic model for request validation
class MinerboardRequest(BaseModel):
    uid: int
    hotkey: str
    hash: str
    block: int
    admin_key: Optional[str] = "admin_key"

# Function to check hash integrity
def hash_check(request: EvaluateModelRequest) -> bool:
    hotkey_hash_matches = int(request.hash) == regenerate_hash(
        request.repo_namespace,
        request.repo_name,
        request.chat_template_type,
        request.hotkey,
    )
    return hotkey_hash_matches

# Function to update the status of a leaderboard entry to failed
def update_failure(new_entry, failure_notes):
    if new_entry["status"] == StatusEnum.FAILED:
        return new_entry  # No operation if already failed
    new_entry["status"] = StatusEnum.FAILED
    new_entry["notes"] = failure_notes
    return new_entry

# Function to mark an entry as completed
def update_completed(new_entry, failure_notes):
    if new_entry["status"] == StatusEnum.FAILED:
        return new_entry  # No operation if already failed
    new_entry["status"] = StatusEnum.COMPLETED
    new_entry["notes"] = failure_notes
    return new_entry

# Invalid block range for evaluations
INVALID_BLOCK_START = 3840700
INVALID_BLOCK_END = 5112345

# Function to insert or update a record in Supabase
def upsert_row_supabase(row):
    app.state.supabase_client.table("leaderboard").upsert(row).execute()

# Main function to start the server and manage processing
def start():
    import argparse

    parser = argparse.ArgumentParser(description="Run the server")
    parser.add_argument("--main-api-port", type=int, default=8000, help="Port for the main API")
    parser.add_argument(
        "--queues",
        type=int,
        default=1,
        help="Specify the number of queues to start (default: 1)",
    )
    parser.add_argument(
        "--worker",
        action="store_true",
        help="Run only the worker processes without the API server",
    )
    args = parser.parse_args()

    num_queues = args.queues
    MAIN_API_PORT = args.main_api_port
    app.state.event_logger_enabled = False

    # Initialize event logger
    try:
        event_logger = EventLogger()
        app.state.event_logger = event_logger
        app.state.event_logger_enabled = True
    except Exception as e:
        logger.warning(f"Failed to create event logger: {e}")

    # Initialize Supabase client
    try:
        app.state.supabase_client = supabaser.supa_client()
    except Exception as e:
        logger.warning(f"Failed to create Supabase client: {e}")
    
    # Start evaluation processes
    processes = []
    stagger_seconds = 2
    try:
        logger.info(f"Starting {num_queues} evaluation threads")
        processes = start_staggered_queues(num_queues, stagger_seconds)
        while True:
            time.sleep(60)
            print(f"Current time: {datetime.datetime.now()}")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping...")
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
    finally:
        logger.info("Stopping evaluation thread")
        for process in processes:
            process.terminate()
            process.join()

# Entry point for the application to start
if __name__ == "__main__":
    start()
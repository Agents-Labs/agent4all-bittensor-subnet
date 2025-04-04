# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 const

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import datetime as dt  # For date and time manipulation
import time              # For sleep functionality
import argparse          # For command-line argument parsing
import requests          # For making HTTP requests

from common.data import ModelId  # Importing ModelId from common.data

import random
import torch             # For PyTorch functionality
from typing import cast, Any, Dict  # For type hinting
import constants         # Constants used throughout the script
import traceback         # For error traceback
import bittensor as bt    # Bittensor library for blockchain interaction
from bittensor import Subtensor  # Importing Subtensor class from Bittensor
from bittensor.core.chain_data import decode_account_id  # Function to decode account IDs

from common.scores import StatusEnum, Scores  # Importing status and score enums
from utilities.local_metadata import LocalMetadata  # Managing local metadata
import os                # For OS functionalities

from utilities.event_logger import EventLogger  # Logging utility
from utilities.validation_utils import regenerate_hash  # Hash utilities if needed

# Initialize LocalMetadata with placeholders for commit and version
l = LocalMetadata(commit="x", btversion="x")
SKIP_BLOCK = 5207777  # Define a threshold block number to skip entries

# Define Hugging Face API endpoint
ENDPOINT = "https://huggingface.co"
REPO_TYPES = ["model", "dataset", "space"]  # Types of repositories available on Hugging Face

# Retrieve the Hugging Face access token from environment variables
hf_token = os.environ["HF_ACCESS_TOKEN"]

def extract_raw_data(data):
    """Extract raw data from the API response.

    Args:
        data (dict): The response data.

    Returns:
        str: The extracted raw data as a string, or None if not found.
    """
    try:
        # Navigate to the fields in the response
        fields = data.get('info', {}).get('fields', ())
        
        # Check the first element's structure to find the 'Raw' key
        if fields and isinstance(fields[0], tuple) and isinstance(fields[0][0], dict):
            raw_dict = fields[0][0]
            raw_key = next((k for k in raw_dict.keys() if k.startswith('Raw')), None)
            
            if raw_key and raw_dict[raw_key]:
                # Convert the tuple of integers to string
                numbers = raw_dict[raw_key][0]
                result = ''.join(chr(x) for x in numbers)
                return result
    except (IndexError, AttributeError):
        pass  # Handle potential errors gracefully

    return None  # Return None if no valid data was found

def push_minerboard(
    hash: str,
    uid: int,
    hotkey: str,
    block: int,
    config,
    local_metadata: LocalMetadata,
    retryWithRemote: bool = False,
) -> None:
    """Push minerboard information to validation endpoint.

    Args:
        hash (str): The hash of the model.
        uid (int): The unique identifier for the model.
        hotkey (str): The hotkey associated with the model.
        block (int): The block number.
        config: Configuration object containing various settings.
        local_metadata (LocalMetadata): Instance of local metadata.
        retryWithRemote (bool): Flag to retry with remote validation.
    """
    # Select validation endpoint based on configuration
    if config.use_local_validation_api and not retryWithRemote:
        validation_endpoint = f"http://localhost:{config.local_validation_api_port}/minerboard_update"
    else:
        validation_endpoint = f"{constants.VALIDATION_SERVER}/minerboard_update"

    # Construct the payload to send
    payload = {
        "hash": hash,
        "uid": uid,
        "hotkey": hotkey,
        "block": block,
    }

    # Build headers for the request using local metadata
    headers = {
        "Git-Commit": str(local_metadata.commit),
        "Bittensor-Version": str(local_metadata.btversion),
        "UID": str(local_metadata.uid),
        "Hotkey": str(local_metadata.hotkey),
        "Coldkey": str(local_metadata.coldkey),
    }

    # Add admin key if available
    if os.environ.get("ADMIN_KEY", None) not in [None, ""]:
        payload["admin_key"] = os.environ["ADMIN_KEY"]

    # Make the POST request to the validation endpoint
    try:
        response = requests.post(validation_endpoint, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except Exception as e:
        print(e)  # Print the error for debugging

class ModelQueue:
    @staticmethod
    def config():
        """Parse command-line arguments and return configuration object."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--netuid", type=str, default=constants.SUBNET_UID, help="The subnet UID.")
        parser.add_argument(
            "--use-local-validation-api",
            action="store_true",
            help="Use a local validation API",
        )
        parser.add_argument(
            "--immediate",
            action="store_true",
            help="Trigger queue immediately",
        )
        parser.add_argument(
            "--local-validation-api-port",
            type=int,
            default=8000,
            help="Port for local validation API",
        )

        # Add arguments from Bittensor configuration
        bt.subtensor.add_args(parser)
        bt.wallet.add_args(parser)
        bt.axon.add_args(parser)
        config = bt.config(parser)
        return config

    def __init__(self):
        """Initialize ModelQueue and its components."""
        self.config = ModelQueue.config()  # Get configuration settings
        self.netuid = self.config.netuid or 11  # Set the subnet UID

        # Initialize Bittensor related objects
        self.subtensor = bt.subtensor(config=self.config)  # Subtensor for blockchain interaction
        self.metagraph = self.subtensor.metagraph(self.config.netuid)  # Metagraph for model metadata
        logfilepath = "/tmp/modelq/{time:UNIX}.log"  # Log file path 
        self.logger = EventLogger(
            filepath=logfilepath,
            level="INFO",  # Log level for event logger
            stderr=True,
        )
        self.logger.info(f"Starting model queue with config: {self.config}")  # Log initial config information

    def forever(self):
        """Run the model queue continuously at regular intervals."""
        while True:
            now = dt.datetime.now()
            # Calculate the next 5-minute mark
            minutes_until_next_epoch = 5 - (now.minute % 5)
            next_epoch_minute_mark = now + dt.timedelta(minutes=minutes_until_next_epoch)
            next_epoch_minute_mark = next_epoch_minute_mark.replace(second=0, microsecond=0)
            sleep_time = (next_epoch_minute_mark - now).total_seconds()
            self.logger.info(f"sleeping for {sleep_time}")  # Log sleep time
            if not self.config.immediate:
                time.sleep(sleep_time)  # Sleep until the next epoch

            try:
                self.load_latest_metagraph()  # Load the latest metagraph data
            except Exception as e:
                self.logger.error(f"failed to queue {e}")  # Log any exceptions encountered

    def build_commit_data(self) -> Dict[str, Any]:
        """Build commitment data from the blockchain.

        Returns:
            commitments (Dict[str, Any]): A dictionary of commitments.
        """
        max_retries = 10  # Set maximum retries for fetching data
        base_delay = 1.5  # Base delay for retries in seconds
        commitments = {}
        raw_commmitments = None  # Placeholder for raw commitments

        for attempt in range(max_retries):
            try:
                # First try fetching data using self.subtensor
                try:
                    raw_commmitments = self.subtensor.query_map(
                        module="Commitments",
                        name="CommitmentOf",
                        params=[self.config.netuid])
                except Exception as e:
                    bt.logging.warning(f"Failed to fetch metadata with self.subtensor: {e}, trying dedicated subtensor")
                    # Fall back to using a dedicated subtensor
                    dedicated_subtensor = None
                    try:
                        network = random.choice(["finney", "subvortex", "latent-lite"])
                        dedicated_subtensor = Subtensor(network=network)
                        bt.logging.warning(f"Created dedicated subtensor for metadata fetch: {dedicated_subtensor}")
                        raw_commmitments = dedicated_subtensor.query_map(
                        module="Commitments",
                        name="CommitmentOf",
                        params=[self.config.netuid])
                    finally:
                        # Ensure the dedicated subtensor is closed after use
                        if dedicated_subtensor is not None:
                            try:
                                dedicated_subtensor.close()
                            except Exception as close_error:
                                bt.logging.error(f"Error closing dedicated subtensor: {close_error}")
            except Exception as e:
                # Handle retries with exponential backoff
                delay = base_delay ** attempt
                if attempt < max_retries - 1:  # Don't log "retrying" on the last attempt
                    bt.logging.error(f"Attempt {attempt + 1}/{max_retries} failed to fetch data : {e}")
                    bt.logging.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    bt.logging.error(f"All attempts failed to fetch data : {e}")
                    raise e  # Raise exception if all attempts fail

        if raw_commmitments is None:
            raise Exception("Failed to fetch raw commitments from chain")  # Raise if data is still None

        # Process raw commitments into a structured dictionary
        commitments = {}
        for key, value in raw_commmitments:
            try:
                hotkey = decode_account_id(key[0])  # Decode account ID
                body = cast(dict, value.value)  # Cast to dictionary
                chain_str = extract_raw_data(body)  # Extract raw data
                commitments[str(hotkey)] = {"block": body["block"], "chain_str": chain_str}  # Store commitments
            except Exception as e:
                bt.logging.error(f"Failed to decode commitment for hotkey {hotkey}: {e}")
                continue  # Continue on error

        return commitments  # Return the commitments found

    def load_latest_metagraph(self):
        """Load the latest metagraph information and process each model."""
        metagraph = self.subtensor.metagraph(self.netuid)  # Get current metagraph
        all_uids = metagraph.uids.tolist()  # Get list of all UIDs

        commitments = self.build_commit_data()  # Fetch the commitment data

        # Initialize counters for logging purposes
        queued = 0
        failed = 0
        no_metadata = 0
        completed = 0

        for uid in all_uids:  # Iterate through each UID in the metagraph
            try:
                hotkey = metagraph.hotkeys[uid]  # Get the hotkey for this UID
                commit_data = commitments.get(hotkey)  # Get corresponding commit data
                if commit_data is None:
                    no_metadata += 1  # Increment no metadata count
                    self.logger.info(f"NO_METADATA : uid: {uid} hotkey : {hotkey}")
                    continue  # Skip if no metadata

                model_id = ModelId.from_compressed_str(commit_data["chain_str"])  # Create a ModelId instance from chain_str
                block = commit_data["block"]  # Get the block number

                if block < SKIP_BLOCK:  # Check if the block is below the threshold
                    self.logger.info(f"SKIP_ENTRY : uid: {uid} hotkey : {hotkey}")
                    continue  # Skip if below threshold

                # Check model score and status
                result = self.check_model_score(
                    namespace=model_id.namespace,  # Extracting model metadata
                    name=model_id.name,
                    hash=model_id.hash,
                    template=model_id.chat_template,
                    block=block,
                    hotkey=hotkey,
                    config=self.config,
                    retryWithRemote=True,  # Allow remote retry
                )
                
                # Log the result of the status check
                stats = f"{result.status} : uid: {uid} hotkey : {hotkey} block: {block} model_metadata : {model_id}"
                self.logger.info(stats)

                # Increment counters based on status result
                if result.status == StatusEnum.FAILED:
                    failed += 1

                if result.status == StatusEnum.QUEUED:
                    self.logger.info(f"QUEUED: {hotkey}")
                    queued += 1

                if result.status == StatusEnum.COMPLETED:
                    completed += 1

                # Push results to minerboard
                push_minerboard(
                    hash=model_id.hash,
                    uid=uid,
                    hotkey=hotkey,
                    block=block,
                    local_metadata=l,  # Using local metadata for identification
                    config=self.config,
                    retryWithRemote=True,  # Allow remote retry
                )

            except Exception as e:
                self.logger.error(f"exception for uid {uid} : {e}")  # Log exception encountered
                continue  # Continue processing for other UIDs

        # Log summary of the processing results
        self.logger.info(f"no_metadata {no_metadata} queued {queued} failed {failed} completed {completed}")

    def check_model_score(
        self,
        namespace,
        name,
        hash,
        template,
        block,
        hotkey,
        config,
        retryWithRemote: bool = False,
    ) -> Scores:
        """Check the score of the model using validation API.

        Args:
            namespace (str): The namespace of the model.
            name (str): The name of the model.
            hash (str): The hash of the model.
            template (str): The template type.
            block (int): The block number.
            hotkey (str): The hotkey associated with the model.
            config: Configuration object.
            retryWithRemote (bool): Flag to retry with remote validation.

        Returns:
            Scores: An instance containing the score and status of the model.
        """
        # Determine the appropriate validation endpoint
        if config.use_local_validation_api and not retryWithRemote:
            validation_endpoint = f"http://localhost:{config.local_validation_api_port}/check_model"
        else:
            validation_endpoint = f"{constants.VALIDATION_SERVER}/check_model"

        # Construct the payload for the validation request
        payload = {
            "repo_namespace": namespace,
            "repo_name": name,
            "hash": hash,
            "chat_template_type": template,
            "block": block,
            "hotkey": hotkey,
        }
        score_data = Scores()  # Create a Scores instance

        # Add admin key if available
        if os.environ.get("ADMIN_KEY", None) not in [None, ""]:
            payload["admin_key"] = os.environ["ADMIN_KEY"]

        result = None

        # Make POST request to the validation endpoint
        try:
            response = requests.post(validation_endpoint, json=payload)  # Send the request
            response.raise_for_status()  # Raise an error for HTTP failures
            result = response.json()  # Parse JSON response
            if result is None:
                raise RuntimeError(f"No leaderboard entry exists at this time for {payload}")

            status = StatusEnum.from_string(result["status"])  # Extract status from response
            score_data.status = status  # Update the score data status
            print(result)  # Print result for debugging
        except Exception as e:
            self.logger.error(f"Failed to get score and status from API for {namespace}/{name} {result} {e}")
            score_data.status = StatusEnum.FAILED  # Set status to FAILED on exception

        return score_data  # Return the score data with status


if __name__ == "__main__":
    q = ModelQueue()  # Instantiate ModelQueue
    q.forever()  # Start the model processing loop
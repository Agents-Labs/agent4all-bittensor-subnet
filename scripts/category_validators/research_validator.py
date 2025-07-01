#!/usr/bin/env python3
"""
Agent4All Research Validator
Specialized validator for research tasks
"""

import os
import sys
import time
import logging
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import bittensor as bt
from neurons.validator import Validator
from category_registry import get_category_info
from scripts.utils.common_functions import CategoryManager, PerformanceTracker, EvaluationEngine

class ResearchValidator(Validator):
    """Specialized validator for research category"""
    def __init__(self, config=None):
        super().__init__(config=config)
        self.category = "research"
        self.category_info = get_category_info(self.category)
        self.tracker = PerformanceTracker(self.category)
        self.evaluator = EvaluationEngine(CategoryManager().get_category_config(self.category))
        logging.info(f"Initialized research validator")

    async def evaluate_research_response(self, response, expected_output=None):
        start_time = time.time()
        try:
            score = await self.evaluator.evaluate_response(
                response.dummy_output,
                expected_output=expected_output,
                task_type=getattr(response, 'task_type', 'default')
            )
            self.tracker.update_metrics(time.time() - start_time, True, score)
            return score
        except Exception as e:
            self.tracker.update_metrics(time.time() - start_time, False, 0.0)
            return 0.0

    async def forward(self):
        try:
            miner_uids = self.get_random_uids(k=self.config.neuron.sample_size)
            responses = await self.dendrite(
                axons=[self.metagraph.axons[uid] for uid in miner_uids],
                synapse=self.create_synapse(),
                deserialize=True,
            )
            scores = []
            for response in responses:
                if response.dendrite.status_code == 200:
                    score = await self.evaluate_research_response(response)
                    scores.append(score)
                else:
                    scores.append(0.0)
            self.update_scores(scores, miner_uids)
        except Exception as e:
            logging.error(f"Validator error: {e}")

    def create_synapse(self):
        from template.protocol import Dummy
        return Dummy(
            dummy_input=self.step,
            category=self.category,
            task_type="default",
            parameters={}
        )

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agent4All Research Validator")
    parser.add_argument("--wallet.name", default="agent4all_coldkey", help="Wallet name")
    parser.add_argument("--wallet.hotkey", default="research_validator_hotkey", help="Wallet hotkey")
    parser.add_argument("--subtensor.network", default="test", help="Bittensor network")
    parser.add_argument("--neuron.device", default="cpu", help="Device to use")
    parser.add_argument("--neuron.sample_size", default=16, type=int, help="Sample size")
    parser.add_argument("--logging.level", default="INFO", help="Logging level")
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.logging.level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    validator = ResearchValidator()
    try:
        validator.run()
    except KeyboardInterrupt:
        logging.info("Validator stopped by user")
    except Exception as e:
        logging.error(f"Validator error: {e}")

if __name__ == "__main__":
    main()

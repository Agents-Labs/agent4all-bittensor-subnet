#!/usr/bin/env python3
"""
Agent4All Programming Miner
Specialized miner for programming tasks
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import bittensor as bt
from neurons.miner import Miner
from category_registry import get_category_info
from scripts.utils.common_functions import CategoryManager, PerformanceTracker

class ProgrammingMiner(Miner):
    """Specialized miner for programming category"""
    def __init__(self, config=None):
        super().__init__(config=config)
        self.category = "programming"
        self.category_info = get_category_info(self.category)
        self.tracker = PerformanceTracker(self.category)
        logging.info(f"Initialized programming miner")

    async def process_programming_request(self, synapse):
        start_time = time.time()
        try:
            request_data = {
                "input": synapse.dummy_input,
                "category": self.category,
                "task_type": getattr(synapse, 'task_type', 'default'),
                "parameters": getattr(synapse, 'parameters', {})
            }
            result = await self.handle_programming_task(request_data)
            response_time = time.time() - start_time
            self.tracker.update_metrics(response_time, True)
            synapse.dummy_output = result
            synapse.category = self.category
            synapse.response_time = response_time
            synapse.success = True
        except Exception as e:
            synapse.dummy_output = f"Error: {str(e)}"
            synapse.success = False
            self.tracker.update_metrics(time.time() - start_time, False)
        return synapse

    async def handle_programming_task(self, request_data):
        return f"Programming task completed for: {request_data['input']}"

    async def forward(self, synapse):
        return await self.process_programming_request(synapse)

    async def blacklist(self, synapse):
        return False, "Request accepted"

    async def priority(self, synapse):
        return 1.0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agent4All Programming Miner")
    parser.add_argument("--wallet.name", default="agent4all_coldkey", help="Wallet name")
    parser.add_argument("--wallet.hotkey", default="programming_hotkey", help="Wallet hotkey")
    parser.add_argument("--subtensor.network", default="test", help="Bittensor network")
    parser.add_argument("--neuron.device", default="cpu", help="Device to use")
    parser.add_argument("--logging.level", default="INFO", help="Logging level")
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.logging.level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    miner = ProgrammingMiner()
    try:
        miner.run()
    except KeyboardInterrupt:
        logging.info("Miner stopped by user")
    except Exception as e:
        logging.error(f"Miner error: {e}")

if __name__ == "__main__":
    main()

# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


import time
import category_registry
import importlib

# Bittensor
import bittensor as bt

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron

# Bittensor Validator Template:
from template.validator import forward


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)
        bt.logging.info("load_state()")
        self.load_state()
        # Use approved categories from registry
        self.supported_categories = category_registry.get_categories()
        if config and hasattr(config, 'categories'):
            self.supported_categories = config.categories

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        # TODO(developer): Rewrite this function based on your protocol definition.
        # Filter miners by supported categories
        miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
        filtered_uids = []
        for uid in miner_uids:
            if self.metagraph.axons[uid].category in self.supported_categories:
                filtered_uids.append(uid)
        if not filtered_uids:
            bt.logging.warning("No miners found in supported categories.")
            return
        responses = await self.dendrite(
            axons=[self.metagraph.axons[uid] for uid in filtered_uids],
            synapse=Dummy(dummy_input=self.step, agent_name="validator_agent", agent_type="validator", agent_description="Validator agent for scoring"),
            deserialize=True,
        )
        bt.logging.info(f"Received responses: {responses}")

        # Assess miners based on utility-based ranking factors
        for response in responses:
            accuracy = response.dummy_output == response.dummy_input * 2
            latency = time.time() - response.dummy_input
            uptime = response.is_online() if hasattr(response, 'is_online') else True
            user_feedback = response.user_feedback if response.user_feedback is not None else 0.0

            # Calculate ranking based on factors
            ranking = (accuracy * 0.4 + (1 / (1 + latency)) * 0.3 + uptime * 0.2 + user_feedback * 0.1)
            response.ranking = ranking

        rewards = get_rewards(self, query=self.step, responses=responses)
        bt.logging.info(f"Scored responses: {rewards}")
        self.update_scores(rewards, filtered_uids)
        time.sleep(5)

        # Category-specific evaluation logic
        for response in responses:
            category = response.category
            # Dynamically load plugin if available
            try:
                plugin = importlib.import_module(f"category_plugins.{category.replace('-', '_')}")
                response.ranking *= plugin.evaluate(response)
            except ModuleNotFoundError:
                bt.logging.info(f"No plugin for category: {category}, using default ranking.")

        # Update rewards based on category-specific evaluations
        rewards = get_rewards(self, query=self.step, responses=responses)
        bt.logging.info(f"Updated scored responses: {rewards}")
        self.update_scores(rewards, filtered_uids)

        # Integrate with live frontend for agent discovery and feedback
        self.push_to_frontend(responses)
        self.ingest_feedback()

        # Implement solid validator incentives
        self.distribute_incentives(rewards)

    def push_to_frontend(self, responses):
        bt.logging.info("Pushing agent/category info to frontend.")
        # Stub: Implement actual push logic

    def ingest_feedback(self):
        bt.logging.info("Ingesting user feedback from frontend.")
        # Stub: Implement actual feedback ingestion

    def approve_pending_categories(self):
        pending = category_registry.get_categories(status="pending")
        for cat in pending:
            # Minimal auto-approve for demo
            category_registry.approve_category(cat)
        bt.logging.info(f"Approved pending categories: {pending}")

    def distribute_incentives(self, rewards):
        """
        Distributes incentives to validators based on their performance.
        """
        bt.logging.info("Distributing incentives to validators.")
        # Logic to distribute incentives


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(5)

# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

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

import time
import typing
import bittensor as bt
import category_registry
import os
import re
from collections import defaultdict
from typing import Dict

# Bittensor Miner Template:
import template

# import base miner class which takes care of most of the boilerplate
from template.base.miner import BaseMinerNeuron


class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)
        
        # Set agent name and type
        self.agent_name = "agent4all_miner"
        self.agent_type = "miner"
        self.agent_description = "Agent4All Bittensor Miner"
        
        # Get available categories first
        self.available_categories = category_registry.get_categories()
        
        # Initialize registered categories
        self.registered_categories = set(self.available_categories)
        
        if config and hasattr(config, 'category') and config.category in self.available_categories:
            self.category = config.category
        else:
            # If not in approved, propose as pending
            if config and hasattr(config, 'category') and config.category:
                self.category = config.category
                if self.category not in self.available_categories:
                    # Propose with minimal metadata
                    category_registry.propose_category(
                        self.category,
                        description=f"Proposed by miner: {self.category}",
                        benchmark="TBD",
                        io_format="TBD",
                        validation_strategy="TBD"
                    )
            else:
                self.category = "data-analyst"

        # Enhanced model submission configuration
        self.model_config = {
            'huggingface_integration': True,
            'model_cache_dir': 'models',
            'max_model_size': 10 * 1024 * 1024 * 1024,  # 10GB
            'supported_formats': ['pytorch', 'tensorflow', 'onnx'],
            'verification_required': True,
            'auto_update': True
        }
        
        # Enhanced registration configuration
        self.registration_config = {
            'namespace_required': True,
            'min_stake': 100,
            'max_models_per_namespace': 10,
            'verification_timeout': 300,  # 5 minutes
            'auto_retry': True,
            'max_retries': 3
        }
        
        # Model registry
        self.model_registry = {
            'models': {},
            'namespaces': {},
            'verification_status': {},
            'update_history': defaultdict(list)
        }
        
        # Performance tracking
        self.performance_metrics = {
            'response_times': defaultdict(list),
            'success_rate': defaultdict(float),
            'error_count': defaultdict(int),
            'model_usage': defaultdict(int),
            'resource_usage': {
                'cpu': [],
                'memory': [],
                'gpu': []
            }
        }
        
        # Security measures
        self.security_config = {
            'rate_limit': {
                'requests_per_minute': 60,
                'burst_limit': 10
            },
            'model_verification': {
                'hash_check': True,
                'signature_verification': True,
                'size_verification': True
            },
            'access_control': {
                'ip_whitelist': [],
                'api_key_required': True
            }
        }
        
        # Initialize model cache
        self.initialize_model_cache()

    def initialize_model_cache(self):
        """Initialize model cache directory."""
        try:
            os.makedirs(self.model_config['model_cache_dir'], exist_ok=True)
        except Exception as e:
            bt.logging.error(f"Failed to initialize model cache: {str(e)}")
    
    def is_online(self) -> bool:
        """Check if the miner is online and operational."""
        try:
            # Basic health check - can be enhanced with more sophisticated checks
            return True
        except Exception:
            return False
    
    def register_model(self, model_info: Dict) -> bool:
        """
        Register a new model with enhanced verification.
        
        Args:
            model_info (Dict): Model information including:
                - model_id: Unique identifier
                - namespace: Model namespace
                - format: Model format
                - source: Model source (e.g., HuggingFace)
                - metadata: Additional model metadata
        
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Validate namespace
            if self.registration_config['namespace_required']:
                if not self.validate_namespace(model_info['namespace']):
                    bt.logging.error(f"Invalid namespace: {model_info['namespace']}")
                    return False
            
            # Check model count per namespace
            if len(self.model_registry['models'].get(model_info['namespace'], {})) >= self.registration_config['max_models_per_namespace']:
                bt.logging.error(f"Namespace {model_info['namespace']} has reached maximum model limit")
                return False
            
            # Verify model
            if self.model_config['verification_required']:
                if not self.verify_model(model_info):
                    bt.logging.error(f"Model verification failed: {model_info['model_id']}")
                    return False
            
            # Register model
            self.model_registry['models'][model_info['model_id']] = {
                'info': model_info,
                'status': 'pending',
                'registered_at': time.time(),
                'last_updated': time.time()
            }
            
            # Update namespace
            if model_info['namespace'] not in self.model_registry['namespaces']:
                self.model_registry['namespaces'][model_info['namespace']] = []
            self.model_registry['namespaces'][model_info['namespace']].append(model_info['model_id'])
            
            bt.logging.info(f"Model registered successfully: {model_info['model_id']}")
            return True
            
        except Exception as e:
            bt.logging.error(f"Model registration failed: {str(e)}")
            return False
    
    def validate_namespace(self, namespace: str) -> bool:
        """Validate model namespace."""
        try:
            # Check namespace format
            if not re.match(r'^[a-zA-Z0-9_-]+$', namespace):
                return False
            
            # Check namespace length
            if len(namespace) < 3 or len(namespace) > 50:
                return False
            
            return True
        except Exception:
            return False
    
    def verify_model(self, model_info: Dict) -> bool:
        """Verify model integrity and authenticity."""
        try:
            # Check model size
            if self.security_config['model_verification']['size_verification']:
                if not self.verify_model_size(model_info):
                    return False
            
            # Verify model hash
            if self.security_config['model_verification']['hash_check']:
                if not self.verify_model_hash(model_info):
                    return False
            
            # Verify model signature
            if self.security_config['model_verification']['signature_verification']:
                if not self.verify_model_signature(model_info):
                    return False
            
            return True
        except Exception as e:
            bt.logging.error(f"Model verification failed: {str(e)}")
            return False
    
    def verify_model_size(self, model_info: Dict) -> bool:
        """Verify model size is within limits."""
        try:
            model_size = self.get_model_size(model_info)
            return model_size <= self.model_config['max_model_size']
        except Exception:
            return False
    
    def verify_model_hash(self, model_info: Dict) -> bool:
        """Verify model hash matches expected value."""
        try:
            if 'hash' not in model_info:
                return False
            
            calculated_hash = self.calculate_model_hash(model_info)
            return calculated_hash == model_info['hash']
        except Exception:
            return False
    
    def verify_model_signature(self, model_info: Dict) -> bool:
        """Verify model signature."""
        try:
            if 'signature' not in model_info:
                return False
            
            # Implement signature verification logic
            return True
        except Exception:
            return False
    
    def get_model_size(self, model_info: Dict) -> int:
        """Get model size in bytes."""
        try:
            # Implement model size calculation
            return 0
        except Exception:
            return 0
    
    def calculate_model_hash(self, model_info: Dict) -> str:
        """Calculate model hash."""
        try:
            # Implement hash calculation
            return ""
        except Exception:
            return ""
    
    def update_model(self, model_id: str, update_info: Dict) -> bool:
        """
        Update model information with verification.
        
        Args:
            model_id (str): Model identifier
            update_info (Dict): Updated model information
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if model_id not in self.model_registry['models']:
                bt.logging.error(f"Model not found: {model_id}")
                return False
            
            # Verify update
            if not self.verify_update(model_id, update_info):
                bt.logging.error(f"Update verification failed: {model_id}")
                return False
            
            # Update model information
            self.model_registry['models'][model_id]['info'].update(update_info)
            self.model_registry['models'][model_id]['last_updated'] = time.time()
            
            # Record update history
            self.model_registry['update_history'][model_id].append({
                'timestamp': time.time(),
                'changes': update_info
            })
            
            bt.logging.info(f"Model updated successfully: {model_id}")
            return True
            
        except Exception as e:
            bt.logging.error(f"Model update failed: {str(e)}")
            return False
    
    def verify_update(self, model_id: str, update_info: Dict) -> bool:
        """Verify model update is valid."""
        try:
            # Implement update verification logic
            return True
        except Exception:
            return False

    async def forward(
        self, synapse: template.protocol.Dummy
    ) -> template.protocol.Dummy:
        """
        Processes the incoming 'Dummy' synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (template.protocol.Dummy): The synapse object containing the 'dummy_input' data.

        Returns:
            template.protocol.Dummy: The synapse object with the 'dummy_output' field set to twice the 'dummy_input' value.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """
        try:
            # TODO(developer): Replace with actual implementation logic.
            # Handle both string and int inputs
            if isinstance(synapse.dummy_input, str):
                try:
                    input_value = int(synapse.dummy_input)
                except ValueError:
                    input_value = 0
            else:
                input_value = synapse.dummy_input
                
            synapse.dummy_output = input_value * 2
            synapse.category = self.category
            synapse.agent_name = self.agent_name
            synapse.agent_type = self.agent_type
            synapse.agent_description = self.agent_description

            # Log utility-based ranking factors
            bt.logging.info(f"Response accuracy: {synapse.dummy_output == synapse.dummy_input * 2}")
            bt.logging.info(f"Latency: {time.time() - synapse.dummy_input}")
            bt.logging.info(f"Uptime & reliability: {self.is_online()}")
            if hasattr(synapse, 'user_feedback') and synapse.user_feedback is not None:
                bt.logging.info(f"User feedback: {synapse.user_feedback}")

            # Apply decay factor for agent ranking
            decay_factor = 0.9  # Example decay factor
            if synapse.ranking is not None:
                synapse.ranking = synapse.ranking * decay_factor
            else:
                synapse.ranking = 1.0

            # Register new agent category if applicable
            if hasattr(self, 'registered_categories') and synapse.category not in self.registered_categories:
                self.register_new_category(synapse.category)

            return synapse
            
        except Exception as e:
            bt.logging.error(f"Error in miner forward pass: {str(e)}")
            # Set default values in case of error
            synapse.dummy_output = 0
            synapse.category = self.category
            synapse.agent_name = self.agent_name
            synapse.agent_type = self.agent_type
            synapse.agent_description = self.agent_description
            return synapse

    def register_new_category(self, category: str):
        """
        Registers a new agent category for review and potential addition to the category registry.

        Args:
            category (str): The new category to register.
        """
        bt.logging.info(f"Registering new category: {category}")
        # Logic to submit the new category for review
        # This could involve sending a proposal to the community for review

    async def blacklist(
        self, synapse: template.protocol.Dummy
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contracted via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (template.protocol.Dummy): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """

        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return True, "Missing dendrite or hotkey"

        # TODO(developer): Define how miners should blacklist requests.
        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
        if (
            not self.config.blacklist.allow_non_registered
            and synapse.dendrite.hotkey not in self.metagraph.hotkeys
        ):
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        # Force validator permit by default for security
        if not self.metagraph.validator_permit[uid]:
            bt.logging.warning(
                f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: template.protocol.Dummy) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (template.protocol.Dummy): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may receive messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return 0.0

        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        priority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: {priority}"
        )
        return priority


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info(f"Miner running... {time.time()}")
            time.sleep(5)

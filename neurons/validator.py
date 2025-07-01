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
import category_registry
import importlib
import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import bittensor as bt
import requests
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
import aiohttp
import websockets
import jwt
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Define custom exception classes
class ValidationError(Exception):
    """Custom validation error for miner responses."""
    def __init__(self, message: str, miner_uid: Optional[int] = None):
        super().__init__(message)
        self.miner_uid = miner_uid

class ConnectionError(Exception):
    """Custom connection error."""
    pass

class TimeoutError(Exception):
    """Custom timeout error."""
    pass

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron

# Bittensor Validator Template:
from template.validator import forward

# Import utility functions
from template.utils.uids import get_random_uids
from template.protocol import Dummy


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
        
        # Enhanced registration and authentication
        self.auth_config = {
            'hotkey_verification': True,
            'coldkey_verification': True,
            'min_stake': 1000,
            'max_concurrent_requests': 32,
            'offline_mode': False
        }
        
        # Enhanced weight management
        self.weight_config = {
            'wait_for_inclusion': True,
            'min_weight': 0.1,
            'max_weight': 1.0,
            'decay_factor': 0.95,
            'performance_threshold': 0.7
        }
        
        # Initialize Prometheus metrics
        self.metrics = {
            'response_time': Histogram('validator_response_time_seconds', 'Response time in seconds'),
            'success_rate': Gauge('validator_success_rate', 'Success rate per miner'),
            'error_count': Counter('validator_error_total', 'Total number of errors'),
            'active_miners': Gauge('validator_active_miners', 'Number of active miners'),
            'category_performance': Gauge('validator_category_performance', 'Performance per category', ['category']),
            'weight_distribution': Gauge('validator_weight_distribution', 'Weight distribution per miner'),
            'authentication_attempts': Counter('validator_auth_attempts', 'Authentication attempts', ['status'])
        }
        
        # Use approved categories from registry
        self.supported_categories = category_registry.get_categories()
        if config and hasattr(config, 'categories'):
            self.supported_categories = config.categories

        # Enhanced performance tracking with Prometheus integration
        self.performance_metrics = {
            'response_times': defaultdict(lambda: {
                'success_rate': 0,
                'avg_response_time': 0,
                'total_requests': 0,
                'last_response': None,
                'consecutive_failures': 0,
                'category_success': defaultdict(int),
                'category_total': defaultdict(int),
                'error_types': defaultdict(int),
                'response_sizes': [],
                'latency_percentiles': defaultdict(list),
                'weight_history': []
            }),
            'network_health': {
                'latency': [],
                'throughput': [],
                'error_rates': defaultdict(list),
                'bandwidth_usage': [],
                'connection_states': defaultdict(str)
            },
            'category_performance': defaultdict(lambda: {
                'avg_score': 0,
                'total_requests': 0,
                'success_rate': 0,
                'response_time_percentiles': defaultdict(float),
                'error_distribution': defaultdict(int)
            })
        }

        # Enhanced secure score storage with timestamps and verification
        self.secure_scores = {}
        self.score_history = defaultdict(lambda: {
            'scores': [],
            'timestamps': [],
            'categories': [],
            'verification_hashes': [],
            'confidence_scores': [],
            'weight_updates': []
        })
        
        # Enhanced routing table with load balancing and failover
        self.routing_table = defaultdict(lambda: {
            'primary_miners': [],
            'backup_miners': [],
            'last_updated': time.time(),
            'load': 0,
            'health_score': 1.0,
            'failover_count': 0,
            'last_failover': None,
            'recovery_status': 'healthy',
            'weight': 1.0
        })
        
        # Enhanced security configuration
        self.security_config = {
            'rate_limit': {
                'requests_per_minute': 60,
                'burst_limit': 10,
                'cooldown_period': 300  # 5 minutes
            },
            'score_thresholds': {
                'min_consistency': 0.7,
                'max_variance': 0.3,
                'min_confidence': 0.8
            },
            'health_checks': {
                'max_consecutive_failures': 3,
                'min_success_rate': 0.8,
                'max_response_time': 5.0,
                'min_uptime': 0.95
            },
            'jwt_secret': 'your-secret-key',  # Replace with secure key
            'token_expiry': 3600  # 1 hour
        }
        
        # Enhanced frontend configuration
        self.frontend_config = {
            'api_endpoint': 'http://localhost:3000/api',
            'ws_endpoint': 'ws://localhost:3000/ws',
            'update_interval': 5,  # seconds
            'batch_size': 100,
            'retry_attempts': 3,
            'timeout': 5,
            'compression': True
        }
        
        # Initialize WebSocket connection
        self.ws = None
        self.ws_connected = False
        
        # Start Prometheus metrics server
        start_http_server(8000)
        
        self.update_routing_table()

    async def connect_websocket(self):
        """Establish WebSocket connection for real-time updates."""
        try:
            self.ws = await websockets.connect(self.frontend_config['ws_endpoint'])
            self.ws_connected = True
            bt.logging.info("WebSocket connection established")
        except Exception as e:
            bt.logging.error(f"WebSocket connection failed: {str(e)}")
            self.ws_connected = False

    async def push_realtime_update(self, data: Dict):
        """Push real-time updates via WebSocket."""
        if not self.ws_connected:
            await self.connect_websocket()
        
        try:
            await self.ws.send(json.dumps(data))
        except Exception as e:
            bt.logging.error(f"WebSocket send failed: {str(e)}")
            self.ws_connected = False

    def generate_jwt_token(self, data: Dict) -> str:
        """Generate JWT token for secure communication."""
        return jwt.encode(
            {
                'data': data,
                'exp': datetime.utcnow() + timedelta(seconds=self.security_config['token_expiry'])
            },
            self.security_config['jwt_secret'],
            algorithm='HS256'
        )

    def verify_jwt_token(self, token: str) -> Dict:
        """Verify JWT token."""
        try:
            return jwt.decode(token, self.security_config['jwt_secret'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

    async def handle_error(self, error: Exception):
        """Enhanced error handling with recovery mechanisms."""
        error_type = type(error).__name__
        self.metrics['error_count'].inc()
        
        # Log error details
        bt.logging.error(f"Validator error: {str(error)}")
        
        # Update error metrics
        if hasattr(error, 'miner_uid'):
            self.performance_metrics['response_times'][error.miner_uid]['error_types'][error_type] += 1
        
        # Implement recovery strategies based on error type
        if isinstance(error, ConnectionError):
            await self.handle_connection_error(error)
        elif isinstance(error, TimeoutError):
            await self.handle_timeout_error(error)
        elif isinstance(error, ValidationError):
            await self.handle_validation_error(error)
        else:
            await self.handle_generic_error(error)
        
        # Update health scores
        self.update_health_scores()

    async def handle_connection_error(self, error: ConnectionError):
        """Handle connection errors with retry logic."""
        if hasattr(error, 'miner_uid'):
            uid = error.miner_uid
            # Use default category since AxonInfo doesn't have category attribute
            category = "data-analyst"  # Default category
            self.routing_table[category]['failover_count'] += 1
            self.routing_table[category]['recovery_status'] = 'recovering'
            
            # Implement exponential backoff
            await asyncio.sleep(min(2 ** self.routing_table[category]['failover_count'], 300))
            
            # Attempt recovery
            if await self.attempt_recovery(uid):
                self.routing_table[category]['recovery_status'] = 'healthy'
            else:
                self.routing_table[category]['recovery_status'] = 'failed'

    async def handle_timeout_error(self, error: TimeoutError):
        """Handle timeout errors with circuit breaker pattern."""
        if hasattr(error, 'miner_uid'):
            uid = error.miner_uid
            # Use default category since AxonInfo doesn't have category attribute
            category = "data-analyst"  # Default category
            
            # Update metrics
            self.performance_metrics['response_times'][uid]['consecutive_failures'] += 1
            
            # Check if circuit should be opened
            if self.performance_metrics['response_times'][uid]['consecutive_failures'] >= self.security_config['health_checks']['max_consecutive_failures']:
                self.routing_table[category]['recovery_status'] = 'circuit_open'
                await self.open_circuit(uid)

    async def handle_validation_error(self, error: ValidationError):
        """Handle validation errors with score adjustment."""
        if hasattr(error, 'miner_uid'):
            uid = error.miner_uid
            # Adjust miner's score
            self.secure_scores[uid] *= 0.8
            # Log validation failure
            bt.logging.warning(f"Validation failed for miner {uid}: {str(error)}")

    async def handle_generic_error(self, error: Exception):
        """Handle generic errors with fallback mechanisms."""
        bt.logging.error(f"Generic error occurred: {str(error)}")
        # Implement fallback logic
        await self.activate_fallback_mechanism()

    async def attempt_recovery(self, uid: int) -> bool:
        """Attempt to recover a failed miner."""
        try:
            # Implement recovery logic
            return True
        except Exception:
            return False

    async def open_circuit(self, uid: int):
        """Open circuit breaker for a problematic miner."""
        # Use default category since AxonInfo doesn't have category attribute
        category = "data-analyst"  # Default category
        if uid in self.routing_table[category]['primary_miners']:
            self.routing_table[category]['primary_miners'].remove(uid)
        if uid in self.routing_table[category]['backup_miners']:
            self.routing_table[category]['backup_miners'].remove(uid)

    async def activate_fallback_mechanism(self):
        """Activate fallback mechanism for system stability."""
        # Implement fallback logic
        pass

    def update_health_scores(self):
        """Update health scores based on recent performance."""
        for category in self.supported_categories:
            for uid in self.routing_table[category]['primary_miners'] + self.routing_table[category]['backup_miners']:
                metrics = self.performance_metrics['response_times'][uid]
                health_score = self.calculate_health_score(metrics)
                self.routing_table[category]['health_score'] = health_score
                
                # Update Prometheus metrics
                self.metrics['success_rate'].set(health_score)
                self.metrics['category_performance'].labels(category=category).set(health_score)

    async def push_to_frontend(self, responses: List):
        """Enhanced frontend integration with real-time updates and compression."""
        try:
            # Prepare data with JWT token
            data = {
                'timestamp': datetime.now().isoformat(),
                'responses': [
                    {
                        'miner_id': response.dendrite.hotkey,
                        'category': getattr(response, 'category', 'data-analyst'),  # Default category
                        'score': self.secure_scores.get(self.metagraph.hotkeys.index(response.dendrite.hotkey), 0),
                        'performance': self.performance_metrics['response_times'][self.metagraph.hotkeys.index(response.dendrite.hotkey)],
                        'health_score': self.routing_table[getattr(response, 'category', 'data-analyst')]['health_score']
                    }
                    for response in responses
                    if response is not None and hasattr(response, 'dendrite') and response.dendrite is not None
                ],
                'network_health': self.performance_metrics['network_health'],
                'category_performance': dict(self.performance_metrics['category_performance'])
            }
            
            # Generate JWT token
            token = self.generate_jwt_token(data)
            
            # Send to frontend API with retry logic
            for attempt in range(self.frontend_config['retry_attempts']):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{self.frontend_config['api_endpoint']}/update",
                            json={'data': data, 'token': token},
                            timeout=self.frontend_config['timeout']
                        ) as response:
                            if response.status == 200:
                                break
                            else:
                                bt.logging.error(f"Failed to push to frontend: {await response.text()}")
                except Exception as e:
                    if attempt == self.frontend_config['retry_attempts'] - 1:
                        raise e
                    await asyncio.sleep(1)
            
            # Push real-time update via WebSocket
            await self.push_realtime_update(data)
            
        except Exception as e:
            bt.logging.error(f"Error pushing to frontend: {str(e)}")
            await self.handle_error(e)

    def verify_response_integrity(self, response) -> bool:
        """Enhanced response integrity verification."""
        try:
            # Basic format check
            if not hasattr(response, 'dummy_output'):
                return False
            
            # Verify response signature
            if hasattr(response, 'signature'):
                if not self.verify_signature(response):
                    return False
            
            # Check response timestamp
            if hasattr(response, 'timestamp'):
                if time.time() - response.timestamp > 30:
                    return False
            
            # Verify response hash
            if hasattr(response, 'hash'):
                calculated_hash = hashlib.sha256(str(response.dummy_output).encode()).hexdigest()
                if calculated_hash != response.hash:
                    return False
            
            # Check response size
            response_size = len(str(response.dummy_output))
            if response_size > 1000000:  # 1MB limit
                return False
            
            return True
        except Exception:
            return False

    def detect_suspicious_pattern(self, history: List[float], new_score: float) -> bool:
        """Enhanced suspicious pattern detection."""
        if len(history) < 3:
            return False
        
        # Check for sudden score changes
        if abs(new_score - history[-1]) > 0.5:
            return True
        
        # Check for repetitive patterns
        if len(set(history[-5:])) == 1 and new_score == history[-1]:
            return True
        
        # Check for linear patterns (potential manipulation)
        if len(history) >= 5:
            x = np.arange(len(history[-5:]))
            y = np.array(history[-5:])
            slope, _ = np.polyfit(x, y, 1)
            if abs(slope) < 0.01:  # Too linear
                return True
        
        # Check for oscillation patterns
        if len(history) >= 6:
            diffs = np.diff(history[-6:])
            if all(abs(d) < 0.01 for d in diffs):  # Too consistent
                return True
        
        return False

    def update_routing_table(self):
        """Enhanced routing table update with load balancing and health checks."""
        current_time = time.time()
        for category in self.supported_categories:
            category_data = self.routing_table[category]
            
            # Update health scores
            for miner_uid in category_data['primary_miners'] + category_data['backup_miners']:
                metrics = self.performance_metrics['response_times'][miner_uid]
                health_score = self.calculate_health_score(metrics)
                category_data['health_score'] = health_score
                
                # Remove unhealthy miners
                if health_score < self.security_config['health_checks']['min_success_rate']:
                    if miner_uid in category_data['primary_miners']:
                        category_data['primary_miners'].remove(miner_uid)
                    if miner_uid in category_data['backup_miners']:
                        category_data['backup_miners'].remove(miner_uid)
            
            # Sort miners by health score and load
            all_miners = category_data['primary_miners'] + category_data['backup_miners']
            sorted_miners = sorted(all_miners, 
                                 key=lambda x: (self.routing_table[category]['health_score'], 
                                              -self.routing_table[category]['load']))
            
            # Update primary and backup lists
            category_data['primary_miners'] = sorted_miners[:3]  # Top 3 as primary
            category_data['backup_miners'] = sorted_miners[3:6]  # Next 3 as backup
            category_data['last_updated'] = current_time

    def calculate_health_score(self, metrics: Dict) -> float:
        """Calculate comprehensive health score for a miner."""
        success_rate = metrics['success_rate']
        response_time = metrics['avg_response_time']
        consecutive_failures = metrics['consecutive_failures']
        
        # Normalize response time (lower is better)
        time_score = max(0, 1 - (response_time / 5.0))  # 5 seconds as max acceptable
        
        # Penalize consecutive failures
        failure_penalty = min(1, consecutive_failures / self.security_config['health_checks']['max_consecutive_failures'])
        
        return (success_rate * 0.6 + time_score * 0.4) * (1 - failure_penalty)

    async def forward(self):
        """Enhanced validator forward pass with comprehensive security and monitoring."""
        try:
            # Generate query and get responses with load balancing
            miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
            filtered_uids = self.route_requests(miner_uids)
            
            if not filtered_uids:
                bt.logging.warning("No suitable miners found for routing.")
                return

            # Update load for selected miners
            for uid in filtered_uids:
                # Use default category since AxonInfo doesn't have category attribute
                category = "data-analyst"  # Default category
                self.routing_table[category]['load'] += 1

            responses = await self.dendrite(
                axons=[self.metagraph.axons[uid] for uid in filtered_uids],
                synapse=Dummy(dummy_input=self.step, agent_name="validator_agent", agent_type="validator", agent_description="Validator agent for scoring"),
                deserialize=True,
            )

            # Check if responses is None or empty
            if responses is None:
                bt.logging.warning("Received None responses from dendrite")
                return
                
            if not responses:
                bt.logging.warning("Received empty responses from dendrite")
                return

            # Process and validate responses with enhanced security
            validated_responses = self.validate_responses(responses)
            
            # Calculate secure scores with anti-manipulation measures
            scores = self.calculate_secure_scores(validated_responses)
            
            # Update comprehensive performance metrics
            self.update_performance_metrics(validated_responses)
            
            # Update routing table based on new performance data
            self.update_routing_table()
            
            # Push to frontend with structured data
            self.push_to_frontend(validated_responses)
            
            # Process user feedback
            self.ingest_feedback()
            
            # Distribute incentives with security checks
            self.distribute_incentives(scores)
            
        except Exception as e:
            bt.logging.error(f"Error in validator forward pass: {str(e)}")
            self.handle_error(e)

    def route_requests(self, miner_uids: List[int]) -> List[int]:
        """
        Routes requests to appropriate miners based on category and performance.
        """
        routed_uids = []
        for uid in miner_uids:
            # Use default category since AxonInfo doesn't have category attribute
            category = "data-analyst"  # Default category
            if category in self.routing_table:
                if self.is_miner_available(uid, category):
                    routed_uids.append(uid)
        return routed_uids

    def is_miner_available(self, uid: int, category: str) -> bool:
        """
        Checks if a miner is available and performing well for a given category.
        """
        if uid not in self.performance_metrics['response_times']:
            return True
        
        metrics = self.performance_metrics['response_times'][uid]
        return (
            metrics.get('success_rate', 0) > 0.8 and
            metrics.get('avg_response_time', float('inf')) < 5.0
        )

    def validate_responses(self, responses: List) -> List:
        """Enhanced response validation with multiple security checks."""
        validated = []
        for response in responses:
            # Check if response is None
            if response is None:
                bt.logging.warning("Received None response from miner")
                continue
                
            if not self.verify_response(response):
                continue
                
            # Check if response has dendrite attribute
            if not hasattr(response, 'dendrite') or response.dendrite is None:
                bt.logging.warning("Response missing dendrite attribute")
                continue
                
            # Check rate limiting
            if self.is_rate_limited(response.dendrite.hotkey):
                bt.logging.warning(f"Rate limit exceeded for miner: {response.dendrite.hotkey}")
                continue
                
            # Verify response integrity
            if not self.verify_response_integrity(response):
                bt.logging.warning(f"Response integrity check failed for miner: {response.dendrite.hotkey}")
                continue
                
            validated.append(response)
            
        return validated

    def verify_response(self, response) -> bool:
        """
        Verifies response integrity and authenticity.
        """
        # Add response verification logic here
        return True

    def calculate_secure_scores(self, responses: List) -> Dict:
        """
        Calculates secure scores with anti-manipulation measures.
        """
        scores = {}
        for response in responses:
            # Check if response is None or missing dendrite
            if response is None or not hasattr(response, 'dendrite') or response.dendrite is None:
                continue
                
            try:
                uid = self.metagraph.hotkeys.index(response.dendrite.hotkey)
            except (ValueError, AttributeError):
                bt.logging.warning(f"Could not find hotkey in metagraph: {getattr(response.dendrite, 'hotkey', 'unknown')}")
                continue
            
            # Calculate base score
            base_score = self.calculate_base_score(response)
            
            # Apply security measures
            secure_score = self.apply_security_measures(base_score, uid)
            
            # Store in secure score history
            self.update_score_history(uid, secure_score)
            
            scores[uid] = secure_score
        
        return scores

    def calculate_base_score(self, response) -> float:
        """
        Calculates base score for a response.
        """
        category = getattr(response, 'category', 'data-analyst')  # Default category
        try:
            plugin = importlib.import_module(f"category_plugins.{category.replace('-', '_')}")
            return plugin.evaluate(response)
        except ModuleNotFoundError:
            return 1.0

    def apply_security_measures(self, score: float, uid: int) -> float:
        """
        Applies security measures to prevent score manipulation.
        """
        # Add rate limiting
        if self.is_rate_limited(uid):
            return score * 0.5
        
        # Add consistency checks
        if not self.is_score_consistent(uid, score):
            return score * 0.8
        
        return score

    def is_rate_limited(self, uid: int) -> bool:
        """
        Checks if a miner is rate limited.
        """
        return False  # Implement rate limiting logic

    def is_score_consistent(self, uid: int, score: float) -> bool:
        """
        Checks if a miner's score is consistent with history.
        """
        if uid not in self.score_history:
            return True
        
        history = self.score_history[uid]['scores']
        if not history:
            return True
        
        avg_score = sum(history) / len(history)
        return abs(score - avg_score) < 0.5

    def update_score_history(self, uid: int, score: float):
        """
        Updates score history for a miner.
        """
        if uid not in self.score_history:
            self.score_history[uid]['scores'] = []
        
        self.score_history[uid]['scores'].append(score)
        if len(self.score_history[uid]['scores']) > 100:  # Keep last 100 scores
            self.score_history[uid]['scores'] = self.score_history[uid]['scores'][-100:]

    def update_performance_metrics(self, responses: List):
        """
        Updates performance metrics for miners.
        """
        for response in responses:
            # Check if response is None or missing dendrite
            if response is None or not hasattr(response, 'dendrite') or response.dendrite is None:
                continue
                
            try:
                uid = self.metagraph.hotkeys.index(response.dendrite.hotkey)
            except (ValueError, AttributeError):
                bt.logging.warning(f"Could not find hotkey in metagraph: {getattr(response.dendrite, 'hotkey', 'unknown')}")
                continue
                
            category = getattr(response, 'category', 'data-analyst')  # Default category
            
            if uid not in self.performance_metrics['response_times']:
                self.performance_metrics['response_times'][uid] = {
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'total_requests': 0
                }
            
            metrics = self.performance_metrics['response_times'][uid]
            metrics['total_requests'] += 1
            metrics['success_rate'] = (metrics['success_rate'] * (metrics['total_requests'] - 1) + 
                                     (1 if self.verify_response(response) else 0)) / metrics['total_requests']

    def ingest_feedback(self):
        """
        Ingests and processes user feedback.
        """
        # Implement feedback ingestion logic
        pass

    def distribute_incentives(self, scores: Dict):
        """Enhanced incentive distribution with security checks."""
        try:
            total_score = sum(scores.values())
            if total_score == 0:
                return
                
            # Apply security checks to scores
            verified_scores = {}
            for uid, score in scores.items():
                if self.verify_score(uid, score):
                    verified_scores[uid] = score
                    
            # Normalize scores
            total_verified = sum(verified_scores.values())
            if total_verified == 0:
                return
                
            # Distribute rewards
            for uid, score in verified_scores.items():
                reward = score / total_verified
                self.update_scores({uid: reward}, [uid])
                
        except Exception as e:
            bt.logging.error(f"Error in incentive distribution: {str(e)}")

    def verify_score(self, uid: int, score: float) -> bool:
        """Verify score validity with multiple checks."""
        if uid not in self.score_history:
            return True
            
        history = self.score_history[uid]['scores']
        if not history:
            return True
            
        # Check for score consistency
        avg_score = sum(history) / len(history)
        if abs(score - avg_score) > self.security_config['score_thresholds']['max_variance']:
            return False
            
        # Check for suspicious patterns
        if self.detect_suspicious_pattern(history, score):
            return False
            
        return True

    def approve_pending_categories(self):
        pending = category_registry.get_categories(status="pending")
        for cat in pending:
            # Minimal auto-approve for demo
            category_registry.approve_category(cat)
        bt.logging.info(f"Approved pending categories: {pending}")

    def verify_authentication(self, synapse) -> bool:
        """Enhanced authentication verification."""
        try:
            # Verify hotkey
            if self.auth_config['hotkey_verification']:
                if not self.verify_hotkey(synapse.dendrite.hotkey):
                    self.metrics['authentication_attempts'].labels(status='hotkey_failed').inc()
                    return False
            
            # Verify coldkey
            if self.auth_config['coldkey_verification']:
                if not self.verify_coldkey(synapse.dendrite.hotkey):
                    self.metrics['authentication_attempts'].labels(status='coldkey_failed').inc()
                    return False
            
            # Check stake
            uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
            if self.metagraph.S[uid] < self.auth_config['min_stake']:
                self.metrics['authentication_attempts'].labels(status='insufficient_stake').inc()
                return False
            
            self.metrics['authentication_attempts'].labels(status='success').inc()
            return True
            
        except Exception as e:
            bt.logging.error(f"Authentication error: {str(e)}")
            self.metrics['authentication_attempts'].labels(status='error').inc()
            return False

    def verify_hotkey(self, hotkey: str) -> bool:
        """Verify hotkey authenticity."""
        try:
            return hotkey in self.metagraph.hotkeys
        except Exception:
            return False

    def verify_coldkey(self, hotkey: str) -> bool:
        """Verify coldkey authenticity."""
        try:
            uid = self.metagraph.hotkeys.index(hotkey)
            return self.metagraph.coldkeys[uid] is not None
        except Exception:
            return False

    def update_weights(self, scores: Dict):
        """Enhanced weight management with wait-for-inclusion."""
        try:
            # Calculate new weights
            new_weights = {}
            total_score = sum(scores.values())
            
            if total_score > 0:
                for uid, score in scores.items():
                    # Apply performance-based weight adjustment
                    performance = self.performance_metrics['response_times'][uid]['success_rate']
                    if performance < self.weight_config['performance_threshold']:
                        score *= performance
                    
                    # Apply time-based decay
                    if uid in self.secure_scores:
                        score *= self.weight_config['decay_factor']
                    
                    new_weights[uid] = max(
                        min(score / total_score, self.weight_config['max_weight']),
                        self.weight_config['min_weight']
                    )
            
            # Update weights with wait-for-inclusion
            if self.weight_config['wait_for_inclusion']:
                self.set_weights(new_weights, wait_for_inclusion=True)
            else:
                self.set_weights(new_weights)
            
            # Update metrics
            for uid, weight in new_weights.items():
                self.metrics['weight_distribution'].set(weight)
                self.performance_metrics['response_times'][uid]['weight_history'].append(weight)
            
        except Exception as e:
            bt.logging.error(f"Error updating weights: {str(e)}")


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(5)

from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class ModelCompetitionConfig:
    """Configuration parameters for model competitions."""

    # The percentage of rewards distributed
    reward_ratio: float
    # Unique identifier for the competition
    competition_identifier: str

# ---------------------------------
# Global Constants.
# ---------------------------------

# Unique identifier for this subnet
CURRENT_SUBNET_UID = 334
# Initial block number for this subnet
CURRENT_SUBNET_START_BLOCK = 2998564
# Base directory for the project
PROJECT_BASE_DIR = Path(__file__).resolve().parent.parent
# Maximum size in bytes for hugging face model repository
MAX_REPO_SIZE_BYTES: int = 72 * 1024 * 1024 * 1024

# Configuration for model competitions
MODEL_COMPETITION_CONFIGS: List[ModelCompetitionConfig] = [
    ModelCompetitionConfig(
        reward_ratio=1.0,
        competition_identifier="competition_1",
    ),
]
PRIMARY_COMPETITION_ID = "competition_1"

# Ensure the total reward ratio sums to 1.0
total_reward = sum(config.reward_ratio for config in MODEL_COMPETITION_CONFIGS)
assert math.isclose(total_reward, 1.0)

# ---------------------------------
# Parameters for Miner/Validator Models.
# ---------------------------------

validator_model_version = 7

# Factor for moving average of validator weights
moving_average_alpha = 0.9
# Scoring temperature for validator models (exponential)
scoring_temperature = 0.005 * 15
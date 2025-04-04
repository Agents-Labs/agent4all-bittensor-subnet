from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
import math

# Constants representing thresholds and factors affecting scores.
CREATIVITY_STEEPNESS = 8  # Steepness of the creativity score adjustment
CREATIVITY_THRESHOLD = 0.5  # Threshold for evaluating creativity

QUALITATIVE_SCORE_THRESHOLD = 0.25  # Minimum threshold for qualitative score
LLM_MODEL_SIZE_THRESHOLD = 0.75  # Size threshold for the LLM model score
LLM_MODEL_SIZE_STEEPNESS = 8  # Steepness factor for model size adjustment
QUALITATIVE_SCORE_WEIGHT = 0.84  # Weight assigned to qualitative score
LATENCY_SCORE_WEIGHT = 0.16  # Weight assigned to latency score
COHERENCE_MINIMUM = 0.95  # Minimum value for coherence to be considered valid
JUDGE_SCORE_THRESHOLD = 0.45  # Threshold for a valid judge score

class StrEnum(str, Enum):
    """String Enum class to support enhanced string functionality."""
    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def from_string(cls, value: str):
        """Convert a string to its corresponding enum member."""
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"{value} is not a valid {cls.__name__}")

class StatusEnum(StrEnum):
    """Enumeration representing the status of the scoring process."""
    QUEUED = "QUEUED"
    PRECHECK = "PRECHECK"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RUNNING = "RUNNING"

class Scores(BaseModel):
    """A model representing various scores for evaluating LLM performance."""
    total_score: float = Field(default=0, description="Total score of the evaluation")
    coherence_score: float = Field(default=0, description="Score indicating the coherence of the model's outputs")
    creativity_score: float = Field(default=0, description="Score reflecting the creativity of the model")
    qualitative_score: float = Field(default=0, description="Qualitative assessment score of the model")
    llm_size_score: float = Field(default=0, description="Score based on the size of the LLM model")
    latency_score: float = Field(default=0, description="Latency score indicating response time of the model")
    post_eval_score: float = Field(default=1, description="Post-evaluation score multiplier")
    judge_score: float = Field(default=0, description="Score from the evaluation judge")

    @staticmethod
    def adjusted_q_score(
        initial_score: float, creativity_score: float, threshold=CREATIVITY_THRESHOLD, steepness=CREATIVITY_STEEPNESS
    ) -> float:
        """Adjust the qualitative score based on creativity levels."""
        # Create an exponential factor affecting the score
        creativity_adjustment = math.exp(steepness * (initial_score - QUALITATIVE_SCORE_THRESHOLD))
        adjusted_score = initial_score / (1 + creativity_adjustment * math.exp(-steepness * (creativity_score - threshold)))
        return adjusted_score

    @staticmethod
    def model_size_adjuster(
        model_size_score: float, threshold=LLM_MODEL_SIZE_THRESHOLD, steepness=LLM_MODEL_SIZE_STEEPNESS
    ) -> float:
        """Adjust model size score based on a defined threshold."""
        if model_size_score < threshold:
            size_penalty = pow(model_size_score / threshold, steepness)
            return size_penalty
        return 1

    def from_response(self, response: Dict[str, Any]) -> 'Scores':
        """Populate score attributes from a given response dictionary."""
        if response is None or len(response) < 1:
            self.total_score = 0
            return self
        self.creativity_score = response.get("creativity_score", 0)
        self.qualitative_score = response.get("qualitative_score", 0)
        self.coherence_score = response.get("coherence_score", 0)
        self.latency_score = response.get("latency_score", 0)
        self.post_eval_score = response.get("post_eval_score", 1)
        self.judge_score = response.get("judge_score", 0)
        return self

    def calculate_total_score(self, adjust_coherence: bool = False) -> float:
        """Calculate the total score based on weighted contributions from various scores."""
        q_score = self.adjusted_q_score(self.qualitative_score, self.creativity_score)
        total_score = (QUALITATIVE_SCORE_WEIGHT * q_score) + (LATENCY_SCORE_WEIGHT * self.latency_score)
        
        # Evaluate coherence score
        given_coherence = 1 if self.coherence_score >= COHERENCE_MINIMUM else 0
        total_score *= given_coherence
        
        # Quick fix for invalid judge scores
        if self.judge_score > 1:
            self.judge_score = 0

        # Apply multipliers if the judge score is above a certain threshold
        if self.judge_score > JUDGE_SCORE_THRESHOLD:
            total_score *= 1.5  
        
        # Set the computed total score
        self.total_score = total_score
        return total_score

    def calculate_new_total_score(self) -> float:
        """Calculate a new score based solely on the judge's score."""
        return self.judge_score


def main():
    import random

    # Initialize a Scores instance with random values for demonstration
    scores = Scores(
        qualitative_score=random.uniform(0.25, 0.70),
        creativity_score=random.uniform(0, 1),
        coherence_score=random.uniform(0, 1),  # Random coherence for demo
        llm_size_score=0,
        latency_score=random.uniform(0, 1),
        post_eval_score=1.0,
    )

    # Display the generated input scores
    print("\nInput Scores:")
    print(f"Qualitative Score: {scores.qualitative_score:.3f}")
    print(f"Creativity Score: {scores.creativity_score:.3f}")
    print(f"Coherence Score: {scores.coherence_score:.3f}")
    print(f"LLM Size Score: {scores.llm_size_score:.3f}")
    print(f"Latency Score: {scores.latency_score:.3f}")

    # Calculate and log adjusted qualitative score
    adjusted_q = scores.adjusted_q_score(scores.qualitative_score, scores.creativity_score)
    print(f"\nAdjusted Qualitative Score: {adjusted_q:.3f}")

    # Determine coherence as either valid (1) or invalid (0)
    coherence_binary = 1 if scores.coherence_score >= COHERENCE_MINIMUM else 0
    print(f"Coherence Binary: {coherence_binary}")

    # Calculate the size adjustment multiplier
    size_multiplier = scores.model_size_adjuster(scores.llm_size_score)
    print(f"Size Multiplier: {size_multiplier:.3f}")

    # Calculate weighted contributions to the total score
    weighted_q = QUALITATIVE_SCORE_WEIGHT * adjusted_q
    weighted_latency = LATENCY_SCORE_WEIGHT * scores.latency_score

    print(f"\nWeighted Scores:")
    print(f"Weighted Qualitative: {weighted_q:.3f}")
    print(f"Weighted Latency: {weighted_latency:.3f}")

    # Compute final score based on the various parameters
    total = scores.calculate_total_score()
    print(f"\nFinal Total Score: {total:.3f}")


if __name__ == "__main__":
    main()

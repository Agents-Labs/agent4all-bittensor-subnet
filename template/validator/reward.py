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
import numpy as np
from typing import List, Optional
import bittensor as bt


def reward(query: int, response: int, category: str = "default", user_feedback: Optional[float] = None) -> float:
    """
    Reward the miner response to the dummy request. This method returns a reward
    value for the miner, which is used to update the miner's score.

    Args:
        query (int): The query sent to the miner.
        response (int): The response from the miner.
        category (str): The category of the request.
        user_feedback (float, optional): User feedback value.

    Returns:
        float: The reward value for the miner.
    """
    # Base reward logic (simplified for demonstration)
    base_reward = 1.0 if response == query * 2 else 0

    # Adjust reward based on user feedback if present
    if user_feedback is not None:
        feedback_weight = 0.5  # Example feedback weight
        base_reward *= (1 + feedback_weight * user_feedback)  # e.g., 1.5x for thumbs up, 0.5x for down

    bt.logging.info(f"In rewards, query val: {query}, response val: {response}, category: {category}, user_feedback: {user_feedback}, rewards val: {base_reward}")
    return base_reward


def get_rewards(
    self,
    query: int,
    responses: List[float],
) -> np.ndarray:
    """
    Returns an array of rewards for the given query and responses.

    Args:
    - query (int): The query sent to the miner.
    - responses (List[float]): A list of responses from the miner.

    Returns:
    - np.ndarray: An array of rewards for the given query and responses.
    """
    # Get all the reward results by iteratively calling your reward() function.
    return np.array([reward(query, response) for response in responses])

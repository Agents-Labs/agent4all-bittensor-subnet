from typing import Any, Dict
from pydantic import BaseModel, Field, PositiveInt

# Constants defining the constraints for metadata and related hashes
MAX_METADATA_BYTES = 128  # The max bytes allowed for metadata on the blockchain
HOTKEY_LENGTH = 40  # Fixed length for a git commit hash
SHA256_BASE_64_LENGTH = 44  # Fixed length for a base64 encoded SHA256 hash
COMPETITION_ID_MAX_LENGTH = 64  # Maximum length for competition identifiers

class ModelMetadata(BaseModel):
    """
    This class holds metadata pertaining to a particular trained model.
    It includes unique identification and the blockchain block number
    on which it was recorded.
    """
    id: str = Field(..., description="A unique identifier for this trained model.")  # Unique model ID
    block: PositiveInt = Field(..., description="Blockchain block number when this model was registered.")  # Block number

    def is_valid(self) -> bool:
        """Check if the model's metadata attributes are valid based on predefined criteria."""
        is_valid_id = len(self.id) <= MAX_METADATA_BYTES  # Validate ID length
        is_valid_block = self.block > 0  # Ensure block number is positive
        return is_valid_id and is_valid_block  # Return combined validity

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model metadata to a dictionary format for easier access and readability."""
        return {
            "model_id": self.id,              # Key for model identifier
            "block_number": self.block        # Key for the associated blockchain block number
        }

# Example usage of the ModelMetadata class
if __name__ == "__main__":
    # Creating an instance of the model metadata
    model_instance = ModelMetadata(id="model_12345", block=15)

    # Validate metadata
    if model_instance.is_valid():
        # Print the dictionary representation of the metadata
        print(model_instance.to_dict())
    else:
        print("Invalid model metadata.")
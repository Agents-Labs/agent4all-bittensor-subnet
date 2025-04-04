import argparse
import hashlib
from typing import Optional, Type

from pydantic import BaseModel, Field, PositiveInt
import bittensor as bt

from common.data import ModelId

from utilities.validation_utils import regenerate_hash

# Default network UID for the Bittensor network
DEFAULT_NETUID = 334

def get_config():
    """Set up argument parsing for configuration options.

    This function creates an argument parser to accept input parameters from
    the command line. The configurations include repository details, 
    chat template, network UID, online status, and model hash. The parsed
    arguments are then returned as a configuration object.

    Returns:
        config: Parsed command line arguments as a configuration object.
    """
    parser = argparse.ArgumentParser()

    # Add argument for repository namespace (Hugging Face organization/repo)
    parser.add_argument(
        "--repo_namespace",
        default="DippyAI",
        type=str,
        help="The hugging face repo id, which should include the org or user and repo name. E.g. jdoe/finetuned",
    )

    # Add argument for the model's repository name
    parser.add_argument(
        "--repo_name",
        default="your-model-here",
        type=str,
        help="The hugging face repo id, which should include the org or user and repo name. E.g. jdoe/finetuned",
    )

    # Add argument for the chat template to be used by the model
    parser.add_argument(
        "--chat_template",
        type=str,
        default="chatml",
        help="The chat template for the model.",
    )

    # Add subnet UID for network identification
    parser.add_argument(
        "--netuid",
        type=str,
        default=f"{DEFAULT_NETUID}",
        help="The subnet UID.",
    )
    
    # Add argument to specify if the model should connect to the network
    parser.add_argument(
        "--online",
        type=bool,
        default=False,
        help="Toggle to make the commit call to the bittensor network",
    )
    
    # Add argument for the model hash of the submission
    parser.add_argument(
        "--model_hash",
        type=str,
        default="d1",
        help="Model hash of the submission",
    )
    
    # Include necessary arguments for wallet and logging from the Bittensor library
    bt.wallet.add_args(parser)
    bt.subtensor.add_args(parser)
    bt.logging.add_args(parser)

    # Parse the arguments and create a configuration namespace
    config = bt.config(parser)
    return config

def register():
    """Handles the registration of the model with the Bittensor network.

    This function retrieves the configuration, sets up the wallet and subtensor,
    generates a unique hash for the model, and logs the details. If configured to 
    be online, it commits the model's information to the Bittensor network.

    The function logs important information at each step to aid in debugging 
    and provide insights into the registration process.
    """
    config = get_config()  # Retrieve configuration from command line arguments
    bt.logging(config=config)  # Set up logging with the retrieved configuration

    # Initialize wallet and subtensor components
    wallet = bt.wallet(config=config)
    subtensor = bt.subtensor(config=config)

    # Retrieve the hotkey address from the wallet
    hotkey = wallet.hotkey.ss58_address
    # Get model configuration details
    namespace = config.repo_namespace
    repo_name = config.repo_name
    chat_template = config.chat_template

    # Generate a unique entry hash for the model
    entry_hash = str(regenerate_hash(namespace, repo_name, chat_template, hotkey))

    # Create a model ID encapsulating model details
    model_id = ModelId(
        namespace=namespace,
        name=repo_name,
        chat_template=chat_template,
        competition_id=config.competition_id,
        hotkey=hotkey,
        hash=entry_hash,
    )
    
    # Compress the model ID into a string for submission
    model_commit_str = model_id.to_compressed_str()

    # Log important registration information
    bt.logging.info("Registering with the following data")
    bt.logging.info(f"Coldkey: {wallet.coldkey.ss58_address}")
    bt.logging.info(f"Hotkey: {hotkey}")
    bt.logging.info(f"repo_namespace: {namespace}")
    bt.logging.info(f"repo_name: {repo_name}")
    bt.logging.info(f"chat_template: {chat_template}")
    bt.logging.info(f"entry_hash: {entry_hash}")
    bt.logging.info(f"Full Model Details: {model_id}")
    bt.logging.info(f"Subtensor Network: {subtensor.network}")
    bt.logging.info(f"model_hash: {config.model_hash}")
    bt.logging.info(f"String to be committed: {model_commit_str}")

    # Attempt to convert the netuid from the config to an integer, using default if it fails
    try:
        netuid = int(config.netuid)
    except ValueError:
        netuid = DEFAULT_NETUID  # Fallback to default netuid if conversion fails
    
    # Ensure netuid is defined; default value used if provided value is zero
    netuid = netuid or DEFAULT_NETUID  

    # If online mode is enabled, attempt to commit to the network
    if config.online:
        try:
            subtensor.commit(wallet, netuid, model_commit_str)
            bt.logging.info(f"Successfully committed {model_commit_str} under {hotkey} on netuid {netuid}")
        except Exception as e:
            print(e)  # Print exception if the commit fails

# Entry point for script execution
if __name__ == "__main__":
    register()
"""
This script runs a validator process and automatically updates it when a new version is released.
Command-line arguments will be forwarded to validator (`neurons/validator.py`), so you can pass
them like this:
    python3 scripts/start_validator.py --wallet.name=my-wallet
Auto-updates are enabled by default and will ensure that the latest version is always running
by pulling the latest version from git and upgrading Python packages. This occurs periodically.
Local changes may prevent the update, but they will be preserved.

The script will use the same virtual environment as the one used to run it. If you want to run
the validator within a virtual environment, run this auto-update script from that environment.

Pm2 is required for this script. This script will start a pm2 process using the name provided by
the --pm2_name argument.
"""

import argparse
import logging
import subprocess
import sys
import time
from datetime import timedelta
from shlex import split
from typing import List
import constants
import datetime

# Configure logging
log = logging.getLogger(__name__)
# Set the interval to check for updates
UPDATES_CHECK_TIME = timedelta(minutes=1)

def get_version() -> str:
    """Extract the version as the current git commit hash.
    
    Returns:
        str: The abbreviated commit hash.
    """
    # Run a git command to get the current commit hash
    result = subprocess.run(
        split("git rev-parse HEAD"),
        check=True,
        capture_output=True,
        cwd=constants.ROOT_DIR,  # Ensure the command runs in the project root directory
    )
    commit = result.stdout.decode().strip()  # Decode the output
    assert len(commit) == 40, f"Invalid commit hash: {commit}"  # Check for the proper hash length
    return commit[:8]  # Return the first 8 characters of the commit hash

def start_validator_process(pm2_name: str, args: List[str], current_version: str = "0") -> subprocess.Popen:
    """Spawn a new Python process running the neurons.validator.
    
    Args:
        pm2_name (str): The name of the pm2 process.
        args (List[str]): The command-line arguments for the validator.
        current_version (str): Current version, defaults to "0" if unspecified.
    
    Returns:
        subprocess.Popen: The started process object.
    """
    assert sys.executable, "Failed to get Python executable"  # Ensure Python interpreter is available

    log.info("Starting validator process with pm2, name: %s", pm2_name)
    # Start the validator using pm2 and the same python interpreter
    process = subprocess.Popen(
        (
            "pm2",
            "start",
            sys.executable,  # Use the same Python executable
            "--name",
            pm2_name,
            "--",
            "-m", "neurons.validator",  # Module to run
            *args,  # Pass any additional arguments
        ),
        cwd=constants.ROOT_DIR,  # Run in the project root directory
    )
    process.pm2_name = pm2_name  # Attach the pm2 name to the process object 
    log.info("Started validator process with pm2, name: %s, version: %s", pm2_name, current_version)

    return process  # Return the started process

import requests
from typing import Dict, Any

def _remote_log(payload: Dict[str, Any]):
    """Log events remotely by sending a payload to the validation server.
    
    Args:
        payload (Dict[str, Any]): The event data to send.
    """
    final_payload = {
        "signature": "x",  # Placeholder for signature
        "payload": payload,  # Incoming payload
        "commit": "x",  # Placeholder for commit info
        "btversion": "x",  # Placeholder for Bittensor version
        "uid": "0",  # Placeholder for user ID
        "hotkey": "x",  # Placeholder for hotkey
        "coldkey": "x",  # Placeholder for coldkey
    }
    event_report_endpoint = f"{constants.VALIDATION_SERVER}/event_report"  # URL for reporting events
    try:
        response = requests.post(event_report_endpoint, json=final_payload)  # Send the payload as JSON
        response.raise_for_status()  # Raise an error for any HTTP errors
        log.info(f"Successfully sent event_report with payload {final_payload}")
    except Exception as e:
        log.error(f"Could not remote log: {e}. This error is ok to ignore if you are a validator")

def stop_validator_process(process: subprocess.Popen) -> None:
    """Stop the validator process using pm2.
    
    Args:
        process (subprocess.Popen): The process to stop.
    """
    subprocess.run(("pm2", "delete", process.pm2_name), cwd=constants.ROOT_DIR, check=True)  # Stop the pm2 process

def pull_latest_version() -> None:
    """Pull the latest version from git.
    
    This uses `git pull --rebase`, which applies local changes on top of updates from the remote repository.
    If there are conflicts, the rebase will be aborted, preserving the local state.
    """
    try:
        subprocess.run(split("git pull --rebase --autostash"), check=True, cwd=constants.ROOT_DIR)
    except subprocess.CalledProcessError as exc:
        log.error("Failed to pull, reverting: %s", exc)  # Log the failure
        _remote_log({"error": str(exc), "message": "Failed to pull from git, reverting"})  # Log the error remotely

        # Abort the rebase if it fails to avoid leaving the repository in an inconsistent state
        subprocess.run(split("git rebase --abort"), check=True, cwd=constants.ROOT_DIR)

def upgrade_packages() -> None:
    """Upgrade Python packages from requirements.txt.
    
    This eventually runs `pip install --upgrade -r requirements.txt` and also upgrades the current package.
    It assumes that no package downgrades are needed, which is unlikely.
    """
    log.info("Upgrading requirements")
    try:
        subprocess.run(
            split(f"{sys.executable} -m pip install -r requirements.txt"),  # Use current Python executable
            check=True,
            cwd=constants.ROOT_DIR,  # Run in the project root directory
        )
    except subprocess.CalledProcessError as exc:
        log.error("Failed to upgrade packages, proceeding anyway. %s", exc)  # Log error but proceed

    log.info("Upgrading packages")
    try:
        subprocess.run(
            split(f"{sys.executable} -m pip install -e ."),  # Install the package in editable mode
            check=True,
            cwd=constants.ROOT_DIR,
        )
    except subprocess.CalledProcessError as exc:
        log.error("Failed to upgrade packages, proceeding anyway. %s", exc)

def main(pm2_name: str, args: List[str]) -> None:
    """Main process loop for the validator that checks for updates and restarts when necessary.
    
    This will check for updates every `UPDATES_CHECK_TIME` and update the validator
    if a new version is available, performed as a simple `git pull --rebase`.
    
    Args:
        pm2_name (str): Name of the PM2 process.
        args (List[str]): Arguments for the validator process.
    """
    # Start the validator process
    validator = start_validator_process(pm2_name, args)
    current_version = get_version()  # Get the current version

    log.info("Current version: %s", current_version)

    try:
        while True:
            pull_latest_version()  # Check for updates
            latest_version = get_version()  # Get the latest version
            log.info("Latest version: %s", latest_version)
            
            # Log the current version against the latest version for monitoring
            _remote_log(
                {
                    "current_version": str(current_version),
                    "latest_version": str(latest_version),
                    "message": "start_validator_check_update",
                }
            )

            if latest_version != current_version:  # Check if there is an update
                log.info(
                    "Upgraded to latest version: %s -> %s",
                    current_version,
                    latest_version,
                )
                upgrade_packages()  # Upgrade packages if new version detected
                current_version = get_version()  # Update current version

                payload = {}
                try:
                    payload["current_version"] = str(current_version)
                    payload["latest_version"] = str(latest_version)
                    payload["time"] = str(datetime.datetime.now(datetime.timezone.utc))  # Log time of upgrade
                except Exception as e:
                    log.error(f"Failed to create payload: {e}")
                    payload["error"] = str(e)  # Capture any errors that occur while creating the payload
                finally:
                    _remote_log(payload)  # Log upgrade event remotely
                stop_validator_process(validator)  # Stop the old validator process
                validator = start_validator_process(pm2_name, args, current_version)  # Start the new process
                current_version = latest_version  # Update to the new current version

            time.sleep(UPDATES_CHECK_TIME.total_seconds())  # Sleep before next update check

    finally:
        stop_validator_process(validator)  # Ensure the validator is stopped on exit

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,  # Set log level to INFO
        format="%(asctime)s %(levelname)s %(message)s",  # Define log message format
        handlers=[logging.StreamHandler(sys.stdout)],  # Output logs to stdout
    )

    parser = argparse.ArgumentParser(
        description="Automatically update and restart the validator process when a new version is released.",
        epilog="Example usage: python start_validator.py --pm2_name 'sn11vali' --wallet_name 'wallet1' --wallet_hotkey 'key123'",
    )

    parser.add_argument("--pm2_name", default="sn11vali", help="Name of the PM2 process.")  # Argument to specify pm2 process name

    flags, extra_args = parser.parse_known_args()  # Parse command-line arguments, allowing unknown arguments

    main(flags.pm2_name, extra_args)  # Run the main function
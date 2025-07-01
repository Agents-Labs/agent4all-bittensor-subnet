#!/usr/bin/env python3
"""
Agent4All Category Validators Launcher
Launches validators for any category
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def launch_validator(category, wallet_name, wallet_hotkey, network="test", device="cpu", sample_size=16):
    """Launch a validator for a specific category"""
    script_path = Path(f"scripts/category_validators/{category}_validator.py")
    
    if not script_path.exists():
        print(f"Error: Validator script not found for category {category}")
        return False
    
    cmd = [
        sys.executable, str(script_path),
        f"--wallet.name={wallet_name}",
        f"--wallet.hotkey={wallet_hotkey}",
        f"--subtensor.network={network}",
        f"--neuron.device={device}",
        f"--neuron.sample_size={sample_size}",
        "--logging.level=INFO"
    ]
    
    print(f"Launching {category} validator...")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error launching {category} validator: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Agent4All Category Validators Launcher")
    parser.add_argument("--category", required=True, help="Category to launch")
    parser.add_argument("--wallet.name", default="agent4all_coldkey", help="Wallet name")
    parser.add_argument("--wallet.hotkey", help="Wallet hotkey (defaults to category_validator_hotkey)")
    parser.add_argument("--subtensor.network", default="test", help="Bittensor network")
    parser.add_argument("--neuron.device", default="cpu", help="Device to use")
    parser.add_argument("--neuron.sample_size", default=16, type=int, help="Sample size")
    
    args = parser.parse_args()
    
    if not args.wallet.hotkey:
        args.wallet.hotkey = f"{args.category}_validator_hotkey"
    
    success = launch_validator(
        args.category,
        args.wallet.name,
        args.wallet.hotkey,
        args.subtensor.network,
        args.neuron.device,
        args.neuron.sample_size
    )
    
    if success:
        print(f"Successfully launched {args.category} validator")
    else:
        print(f"Failed to launch {args.category} validator")
        sys.exit(1)

if __name__ == "__main__":
    main() 
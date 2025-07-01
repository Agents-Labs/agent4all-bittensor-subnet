#!/usr/bin/env python3
"""
Agent4All Category Miners Launcher
Launches miners for any category
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def launch_miner(category, wallet_name, wallet_hotkey, network="test", device="cpu"):
    """Launch a miner for a specific category"""
    script_path = Path(f"scripts/category_miners/{category}_miner.py")
    
    if not script_path.exists():
        print(f"Error: Miner script not found for category {category}")
        return False
    
    cmd = [
        sys.executable, str(script_path),
        f"--wallet.name={wallet_name}",
        f"--wallet.hotkey={wallet_hotkey}",
        f"--subtensor.network={network}",
        f"--neuron.device={device}",
        "--logging.level=INFO"
    ]
    
    print(f"Launching {category} miner...")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error launching {category} miner: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Agent4All Category Miners Launcher")
    parser.add_argument("--category", required=True, help="Category to launch")
    parser.add_argument("--wallet.name", default="agent4all_coldkey", help="Wallet name")
    parser.add_argument("--wallet.hotkey", help="Wallet hotkey (defaults to category_hotkey)")
    parser.add_argument("--subtensor.network", default="test", help="Bittensor network")
    parser.add_argument("--neuron.device", default="cpu", help="Device to use")
    
    args = parser.parse_args()
    
    if not args.wallet.hotkey:
        args.wallet.hotkey = f"{args.category}_hotkey"
    
    success = launch_miner(
        args.category,
        args.wallet.name,
        args.wallet.hotkey,
        args.subtensor.network,
        args.neuron.device
    )
    
    if success:
        print(f"Successfully launched {args.category} miner")
    else:
        print(f"Failed to launch {args.category} miner")
        sys.exit(1)

if __name__ == "__main__":
    main() 
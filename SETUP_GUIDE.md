# Agent4All Bittensor Subnet: Complete Setup Guide

## Quick Start

To run the Agent4All project successfully on the Bittensor network, follow these steps:

### 1. Prerequisites

**System Requirements:**
- Python 3.9+
- 16GB+ RAM
- 100GB+ storage
- Stable internet connection
- Ubuntu 20.04+ (recommended) or Windows 10+

**Install Dependencies:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y git curl build-essential python3-pip

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### 2. Installation

```bash
# Clone repository
git clone https://github.com/Agents-Labs/agent4all-bittensor-subnet
cd agent4all-bittensor-subnet

# Install Bittensor
pip install bittensor

# Install project dependencies
pip install -e .
pip install -r requirements.txt

# Install additional ML libraries
pip install transformers torch torchvision openai anthropic
```

### 3. Wallet Setup

```bash
# Create main wallet (coldkey)
btcli wallet new_coldkey --wallet.name agent4all_coldkey

# Create hotkeys for miner and validator
btcli wallet new_hotkey --wallet.name agent4all_coldkey --wallet.hotkey miner_hotkey
btcli wallet new_hotkey --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey

# Check wallet balance
btcli wallet overview --wallet.name agent4all_coldkey
```

### 4. Network Configuration

```bash
# Choose network (testnet for testing, mainnet for production)
export BT_NETWORK=test  # or main

# Register on subnet (replace NETUID with actual subnet ID)
btcli subnet register --wallet.name agent4all_coldkey --wallet.hotkey miner_hotkey --netuid <NETUID> --subtensor.network $BT_NETWORK
btcli subnet register --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --netuid <NETUID> --subtensor.network $BT_NETWORK

# Stake for validator
btcli stake add --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --amount 1000 --subtensor.network $BT_NETWORK
```

### 5. Running Miners

**Basic Miner:**
```bash
python neurons/miner.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey miner_hotkey \
  --subtensor.network $BT_NETWORK \
  --neuron.category data-analyst \
  --neuron.device cpu \
  --logging.level INFO
```

**GPU Miner:**
```bash
python neurons/miner.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey miner_hotkey \
  --neuron.device cuda \
  --neuron.category programming \
  --logging.level DEBUG
```

**Multi-Category Miner:**
```bash
python neurons/miner.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey miner_hotkey \
  --neuron.categories data-analyst,finance,programming \
  --neuron.max_concurrent_forwards 8
```

### 6. Running Validators

**Basic Validator:**
```bash
python neurons/validator.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey validator_hotkey \
  --subtensor.network $BT_NETWORK \
  --neuron.sample_size 16 \
  --logging.level INFO
```

**High-Performance Validator:**
```bash
python neurons/validator.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey validator_hotkey \
  --neuron.num_concurrent_forwards 64 \
  --neuron.sample_size 32 \
  --neuron.device cuda \
  --logging.level DEBUG
```

### 7. Production Deployment

**Systemd Service (Linux):**
```bash
# Create miner service
sudo tee /etc/systemd/system/agent4all-miner.service << EOF
[Unit]
Description=Agent4All Bittensor Miner
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python neurons/miner.py --wallet.name agent4all_coldkey --wallet.hotkey miner_hotkey --subtensor.network main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable agent4all-miner
sudo systemctl start agent4all-miner
```

**Docker Deployment:**
```bash
# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  miner:
    build: .
    command: python neurons/miner.py --wallet.name agent4all_coldkey --wallet.hotkey miner_hotkey --subtensor.network main
    volumes:
      - ~/.bittensor:/root/.bittensor
    restart: unless-stopped

  validator:
    build: .
    command: python neurons/validator.py --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --subtensor.network main
    volumes:
      - ~/.bittensor:/root/.bittensor
    restart: unless-stopped
EOF

# Run with Docker
docker-compose up -d
```

### 8. Monitoring

**Check Status:**
```bash
# Check miner/validator processes
ps aux | grep "neurons/"

# Check wallet balance
btcli wallet overview --wallet.name agent4all_coldkey

# Check subnet status
btcli subnet list --netuid <NETUID> --subtensor.network $BT_NETWORK

# View logs
tail -f ~/.bittensor/miners/agent4all_miner.log
tail -f ~/.bittensor/validators/agent4all_validator.log
```

**Prometheus Metrics:**
```bash
# Validator exposes metrics on port 8000
curl http://localhost:8000/metrics
```

### 9. Troubleshooting

**Common Issues:**

1. **Connection Problems:**
```bash
# Check network connectivity
btcli subnet list --subtensor.network $BT_NETWORK
```

2. **Registration Issues:**
```bash
# Check if registered
btcli subnet list --netuid <NETUID> --subtensor.network $BT_NETWORK

# Re-register if needed
btcli subnet register --wallet.name agent4all_coldkey --wallet.hotkey miner_hotkey --netuid <NETUID> --subtensor.network $BT_NETWORK --force
```

3. **Performance Issues:**
```bash
# Check system resources
htop
nvidia-smi  # If using GPU

# Enable debug logging
python neurons/miner.py --logging.level DEBUG --logging.format detailed
```

4. **Dependency Issues:**
```bash
# Reinstall Bittensor
pip uninstall bittensor -y
pip install bittensor --upgrade

# Clear cache
pip cache purge
```

### 10. Available Categories

The Agent4All subnet supports these agent categories:
- `data-analyst` - Data analysis and visualization
- `finance` - Financial analysis and advice
- `image` - Image processing and generation
- `image-to-text` - Image captioning and OCR
- `markdown` - Document processing
- `planning` - Project planning and management
- `programming` - Code generation and review
- `recommendation` - Product and content recommendations
- `research` - Research and information gathering
- `shopping` - E-commerce assistance
- `single` - General purpose agents
- `video` - Video processing and analysis
- `websearch` - Web search and browsing
- `wikipedia` - Wikipedia content processing

### 11. Configuration Files

**Miner Config:**
```yaml
# ~/.bittensor/miners/agent4all_miner.yaml
neuron:
  name: agent4all_miner
  category: data-analyst
  device: cpu
  num_concurrent_forwards: 4
  epoch_length: 100
  max_epochs: 1000

wallet:
  name: agent4all_coldkey
  hotkey: miner_hotkey

subtensor:
  network: main
  chain_endpoint: auto

logging:
  level: INFO
  format: detailed
```

**Validator Config:**
```yaml
# ~/.bittensor/validators/agent4all_validator.yaml
neuron:
  name: agent4all_validator
  device: cpu
  num_concurrent_forwards: 32
  sample_size: 16
  epoch_length: 100
  max_epochs: 1000
  moving_average_alpha: 0.1

wallet:
  name: agent4all_coldkey
  hotkey: validator_hotkey

subtensor:
  network: main
  chain_endpoint: auto

logging:
  level: INFO
  format: detailed
```

### 12. Best Practices

**Security:**
- Use strong passwords for wallets
- Keep mnemonic phrases secure and offline
- Regularly update dependencies
- Use firewall rules

**Performance:**
- Monitor system resources
- Use SSD storage
- Optimize network settings
- Choose appropriate categories

**Reliability:**
- Set up automatic restarts
- Use monitoring and alerting
- Keep wallet backups
- Test on testnet first

### 13. Support Resources

- **Documentation**: [docs.agent4all.ai](https://docs.agent4all.ai)
- **GitHub**: [github.com/Agents-Labs/agent4all-bittensor-subnet](https://github.com/Agents-Labs/agent4all-bittensor-subnet)
- **Discord**: [discord.gg/agent4all](https://discord.gg/agent4all)
- **Bittensor Docs**: [docs.bittensor.com](https://docs.bittensor.com)

### 14. Quick Commands Reference

```bash
# Check wallet balance
btcli wallet overview --wallet.name agent4all_coldkey

# List subnets
btcli subnet list --subtensor.network main

# Check metagraph
btcli subnet metagraph --netuid <NETUID> --subtensor.network main

# Transfer TAO
btcli wallet transfer --wallet.name agent4all_coldkey --dest <address> --amount 100

# Stake TAO
btcli stake add --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --amount 1000

# Unstake TAO
btcli stake remove --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --amount 100
```

---

*This setup guide provides the essential steps to run Agent4All on the Bittensor network. For detailed technical information, refer to the white paper and official documentation.* 
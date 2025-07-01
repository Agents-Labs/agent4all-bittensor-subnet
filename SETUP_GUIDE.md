# Agent4All Bittensor Subnet: Complete Setup Guide

## 🚀 Quick Start

To run the Agent4All project successfully on the Bittensor network, follow these comprehensive setup steps:

### 1. Prerequisites

**System Requirements:**
- Python 3.9+ (3.10+ recommended)
- 16GB+ RAM (32GB+ for high-performance)
- 100GB+ storage (SSD recommended)
- Stable internet connection
- Ubuntu 20.04+ (recommended) or Windows 10+
- CUDA-compatible GPU (optional, for GPU acceleration)

**Hardware Recommendations:**
- **CPU**: 8+ cores (16+ for high-performance)
- **RAM**: 32GB+ for production
- **Storage**: 500GB+ SSD
- **Network**: 100Mbps+ upload/download
- **GPU**: NVIDIA RTX 3080+ (optional)

### 2. System Setup

**Ubuntu/Debian:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y git curl build-essential python3-pip python3-venv
sudo apt install -y libssl-dev libffi-dev python3-dev
sudo apt install -y nvidia-cuda-toolkit  # If using GPU

# Install Rust (required for some dependencies)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install Node.js (for some utilities)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 git curl rust node

# Install CUDA (if using GPU)
brew install --cask cuda
```

**Windows:**
```bash
# Install Chocolatey if not installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install python git curl nodejs
```

### 3. Python Environment Setup

```bash
# Clone repository
git clone https://github.com/Agents-Labs/agent4all-bittensor-subnet
cd agent4all-bittensor-subnet

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Bittensor first
pip install bittensor>=9.6.0

# Install project dependencies
pip install -r requirements.txt

# Install additional ML libraries (if needed)
pip install transformers[torch] torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install openai anthropic
```

### 4. Wallet Setup

```bash
# Create main wallet (coldkey)
btcli wallet new_coldkey --wallet.name agent4all_coldkey

# Create hotkeys for different categories
btcli wallet new_hotkey --wallet.name agent4all_coldkey --wallet.hotkey data_analyst_hotkey
btcli wallet new_hotkey --wallet.name agent4all_coldkey --wallet.hotkey finance_hotkey
btcli wallet new_hotkey --wallet.name agent4all_coldkey --wallet.hotkey programming_hotkey
btcli wallet new_hotkey --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey

# Check wallet balance
btcli wallet overview --wallet.name agent4all_coldkey

# Get wallet address for funding
btcli wallet overview --wallet.name agent4all_coldkey --subtensor.network test
```

### 5. Network Configuration

```bash
# Set network environment variable
export BT_NETWORK=test  # Use 'main' for production

# Check available subnets
btcli subnet list --subtensor.network $BT_NETWORK

# Register on subnet (replace NETUID with actual subnet ID)
btcli subnet register --wallet.name agent4all_coldkey --wallet.hotkey data_analyst_hotkey --netuid <NETUID> --subtensor.network $BT_NETWORK
btcli subnet register --wallet.name agent4all_coldkey --wallet.hotkey finance_hotkey --netuid <NETUID> --subtensor.network $BT_NETWORK
btcli subnet register --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --netuid <NETUID> --subtensor.network $BT_NETWORK

# Stake for validator (minimum 1000 TAO)
btcli stake add --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --amount 1000 --subtensor.network $BT_NETWORK

# Check registration status
btcli subnet list --netuid <NETUID> --subtensor.network $BT_NETWORK
```

### 6. Configuration Setup

**Create configuration files:**

```bash
# Create config directory
mkdir -p ~/.bittensor/miners ~/.bittensor/validators

# Create miner config
cat > ~/.bittensor/miners/agent4all_miner.yaml << EOF
neuron:
  name: agent4all_miner
  category: data-analyst
  device: cpu
  num_concurrent_forwards: 4
  epoch_length: 100
  max_epochs: 1000
  max_concurrent_forwards: 8

wallet:
  name: agent4all_coldkey
  hotkey: data_analyst_hotkey

subtensor:
  network: test
  chain_endpoint: auto

logging:
  level: INFO
  format: detailed
EOF

# Create validator config
cat > ~/.bittensor/validators/agent4all_validator.yaml << EOF
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
  network: test
  chain_endpoint: auto

logging:
  level: INFO
  format: detailed
EOF
```

### 7. Running Miners

**Basic Miner:**
```bash
# Launch data analyst miner
python scripts/launch_miner.py --category data-analyst

# Or run directly
python neurons/miner.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey data_analyst_hotkey \
  --subtensor.network test \
  --neuron.category data-analyst \
  --neuron.device cpu \
  --logging.level INFO \
  --netuid 334
```

**GPU Miner:**
```bash
# Launch programming miner with GPU
python scripts/launch_miner.py --category programming --neuron.device cuda

# Or run directly
python neurons/miner.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey programming_hotkey \
  --neuron.device cuda \
  --neuron.category programming \
  --logging.level DEBUG
```

**Multi-Category Miner:**
```bash
# Launch multiple categories
python neurons/miner.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey data_analyst_hotkey \
  --neuron.categories data-analyst,finance,programming \
  --neuron.max_concurrent_forwards 8
```

**Available Categories:**
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

### 8. Running Validators

**Basic Validator:**
```bash
# Launch validator
python scripts/launch_validator.py --category data-analyst

# Or run directly
python neurons/validator.py \
  --wallet.name agent4all_coldkey \
  --wallet.hotkey validator_hotkey \
  --subtensor.network test \
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

### 9. Production Deployment

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
Environment=BT_NETWORK=main
ExecStart=$(pwd)/venv/bin/python neurons/miner.py --wallet.name agent4all_coldkey --wallet.hotkey data_analyst_hotkey --subtensor.network main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create validator service
sudo tee /etc/systemd/system/agent4all-validator.service << EOF
[Unit]
Description=Agent4All Bittensor Validator
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
Environment=BT_NETWORK=main
ExecStart=$(pwd)/venv/bin/python neurons/validator.py --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --subtensor.network main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl enable agent4all-miner
sudo systemctl enable agent4all-validator
sudo systemctl start agent4all-miner
sudo systemctl start agent4all-validator

# Check status
sudo systemctl status agent4all-miner
sudo systemctl status agent4all-validator
```

**Docker Deployment:**
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git curl build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 agent4all
RUN chown -R agent4all:agent4all /app
USER agent4all

# Default command
CMD ["python", "neurons/miner.py"]
EOF

# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  miner:
    build: .
    command: python neurons/miner.py --wallet.name agent4all_coldkey --wallet.hotkey data_analyst_hotkey --subtensor.network main
    volumes:
      - ~/.bittensor:/home/agent4all/.bittensor
    restart: unless-stopped
    environment:
      - BT_NETWORK=main

  validator:
    build: .
    command: python neurons/validator.py --wallet.name agent4all_coldkey --wallet.hotkey validator_hotkey --subtensor.network main
    volumes:
      - ~/.bittensor:/home/agent4all/.bittensor
    restart: unless-stopped
    environment:
      - BT_NETWORK=main
    ports:
      - "8000:8000"  # Prometheus metrics

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
    restart: unless-stopped

volumes:
  grafana-storage:
EOF

# Create Prometheus config
cat > prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'agent4all-validator'
    static_configs:
      - targets: ['validator:8000']
EOF

# Run with Docker
docker-compose up -d
```

### 10. Monitoring and Metrics

**Built-in Monitoring:**
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

# Check system resources
htop
nvidia-smi  # If using GPU
```

**Prometheus Metrics:**
```bash
# Validator exposes metrics on port 8000
curl http://localhost:8000/metrics

# Available metrics:
# - validator_response_time_seconds
# - validator_success_rate
# - validator_error_total
# - validator_active_miners
# - validator_category_performance
# - validator_weight_distribution
```

**Grafana Dashboard:**
```bash
# Access Grafana at http://localhost:3000
# Username: admin
# Password: admin

# Import dashboard from grafana.com or create custom dashboard
```

### 11. Troubleshooting

**Common Issues:**

1. **Connection Problems:**
```bash
# Check network connectivity
btcli subnet list --subtensor.network $BT_NETWORK

# Check firewall settings
sudo ufw status
sudo ufw allow 8091  # Bittensor port
```

2. **Registration Issues:**
```bash
# Check if registered
btcli subnet list --netuid <NETUID> --subtensor.network $BT_NETWORK

# Re-register if needed
btcli subnet register --wallet.name agent4all_coldkey --wallet.hotkey data_analyst_hotkey --netuid <NETUID> --subtensor.network $BT_NETWORK --force
```

3. **Performance Issues:**
```bash
# Check system resources
htop
nvidia-smi  # If using GPU

# Enable debug logging
python neurons/miner.py --logging.level DEBUG --logging.format detailed

# Check memory usage
free -h
df -h
```

4. **Dependency Issues:**
```bash
# Reinstall Bittensor
pip uninstall bittensor -y
pip install bittensor --upgrade

# Clear cache
pip cache purge

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

5. **GPU Issues:**
```bash
# Check CUDA installation
nvidia-smi
nvcc --version

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 12. Security Best Practices

**Wallet Security:**
- Use strong passwords for wallets
- Keep mnemonic phrases secure and offline
- Use hardware wallets for large amounts
- Regularly backup wallet files

**System Security:**
- Keep system updated
- Use firewall rules
- Monitor system logs
- Use non-root user for running services

**Network Security:**
- Use VPN if needed
- Monitor network traffic
- Use secure connections
- Regular security audits

### 13. Performance Optimization

**System Optimization:**
- Use SSD storage
- Optimize network settings
- Monitor resource usage
- Use appropriate hardware

**Bittensor Optimization:**
- Choose appropriate categories
- Optimize batch sizes
- Monitor response times
- Use GPU acceleration

**Monitoring Optimization:**
- Set up alerts
- Monitor metrics
- Track performance
- Optimize configurations

### 14. Support Resources

- **Documentation**: [docs.agent4all.ai](https://docs.agent4all.ai)
- **GitHub**: [github.com/Agents-Labs/agent4all-bittensor-subnet](https://github.com/Agents-Labs/agent4all-bittensor-subnet)
- **Discord**: [discord.gg/agent4all](https://discord.gg/agent4all)
- **Bittensor Docs**: [docs.bittensor.com](https://docs.bittensor.com)
- **Telegram**: [t.me/agent4all](https://t.me/agent4all)

### 15. Quick Commands Reference

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

# Check miner/validator status
btcli subnet list --netuid <NETUID> --subtensor.network main

# View logs
tail -f ~/.bittensor/miners/agent4all_miner.log
tail -f ~/.bittensor/validators/agent4all_validator.log

# Restart services
sudo systemctl restart agent4all-miner
sudo systemctl restart agent4all-validator
```

---

*This setup guide provides comprehensive instructions for running Agent4All on the Bittensor network. For detailed technical information, refer to the white paper and official documentation.* 
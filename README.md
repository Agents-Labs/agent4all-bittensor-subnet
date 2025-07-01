# Agent4All Bittensor Subnet

A specialized Bittensor subnet for AI agents across 14 different categories, providing decentralized AI services with category-specific optimization.

[![GitHub stars](https://img.shields.io/github/stars/Agents-Labs/agent4all-bittensor-subnet)](https://github.com/Agents-Labs/agent4all-bittensor-subnet/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Agents-Labs/agent4all-bittensor-subnet)](https://github.com/Agents-Labs/agent4all-bittensor-subnet/network)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Bittensor wallet with TAO balance
- Git

### Installation
```bash
git clone https://github.com/Agents-Labs/agent4all-bittensor-subnet.git
cd agent4all-bittensor-subnet
pip install -r requirements.txt
```

### Running Miners
```bash
# Launch a data analyst miner
python scripts/launch_miner.py --category data-analyst

# Launch a finance miner  
python scripts/launch_miner.py --category finance

# Launch any other category
python scripts/launch_miner.py --category <category-name>
```

### Running Validators
```bash
# Launch a data analyst validator
python scripts/launch_validator.py --category data-analyst

# Launch a finance validator
python scripts/launch_validator.py --category finance

# Launch any other category
python scripts/launch_validator.py --category <category-name>
```

## 📁 Project Structure

```
agent4all-bittensor-subnet/
├── neurons/                    # Core Bittensor neurons
│   ├── miner.py               # Base miner implementation
│   ├── validator.py           # Base validator implementation
│   └── dataset.py             # Dataset handling
├── template/                   # Bittensor protocol templates
│   ├── protocol.py            # Protocol definitions
│   ├── base/                  # Base classes
│   ├── validator/             # Validator templates
│   └── utils/                 # Utility functions
├── scripts/                    # Category-specific scripts
│   ├── category_miners/       # 14 miner scripts (one per category)
│   ├── category_validators/   # 14 validator scripts (one per category)
│   ├── utils/                 # Shared utilities
│   ├── launch_miner.py        # Miner launcher
│   ├── launch_validator.py    # Validator launcher
│   └── README.md              # Scripts documentation
├── category_registry.py        # Category definitions
├── config.yaml                # Configuration file
├── pyproject.toml             # Python dependencies
├── requirements.txt           # Requirements
├── README.md                  # This file
├── LICENSE                    # License
└── .gitignore                # Git ignore rules
```

## 🎯 Supported Categories

The subnet supports 14 specialized AI agent categories:

1. **data-analyst** - Data analysis and visualization
2. **finance** - Financial analysis and investment advice
3. **image** - Image generation and processing
4. **image-to-text** - Image captioning and OCR
5. **markdown** - Markdown processing and documentation
6. **planning** - Project planning and scheduling
7. **programming** - Code generation and review
8. **recommendation** - Product and content recommendation
9. **research** - Research and information gathering
10. **shopping** - E-commerce and shopping assistance
11. **single** - General purpose conversation
12. **video** - Video processing and analysis
13. **websearch** - Web search and browsing
14. **wikipedia** - Wikipedia content processing

## 🔧 Configuration

### Basic Configuration
Edit `config.yaml` to configure:
- Network settings (testnet/mainnet)
- Wallet configuration
- Neuron parameters
- Category weights

### Wallet Setup
```bash
# Create wallet
btcli wallet new_coldkey --wallet.name agent4all_coldkey
btcli wallet new_hotkey --wallet.name agent4all_coldkey --wallet.hotkey <category>_hotkey

# Register on subnet
btcli subnet register --wallet.name agent4all_coldkey --wallet.hotkey <category>_hotkey --subtensor.network test
```

## 📊 Performance

Each category has specialized:
- **Task processing** optimized for the domain
- **Evaluation metrics** specific to the category
- **Performance tracking** for monitoring
- **Scoring algorithms** for fair rewards

## 🛠️ Development

### Adding New Categories
1. Update `category_registry.py`
2. Create miner script in `scripts/category_miners/`
3. Create validator script in `scripts/category_validators/`
4. Update configuration

### Customizing Scripts
- Modify task handlers in miners
- Adjust evaluation criteria in validators
- Configure scoring weights
- Add category-specific metrics

## 📈 Monitoring

### Built-in Metrics
- Response times
- Success rates
- Score distributions
- Error tracking

### Logging
All scripts support configurable logging:
```bash
--logging.level DEBUG|INFO|WARNING|ERROR
```

## 🔗 Networks

- **Testnet**: `--subtensor.network test` (default)
- **Mainnet**: `--subtensor.network main`
- **Local**: `--subtensor.network local`

## 🚨 Troubleshooting

### Common Issues
1. **Wallet errors**: Check balance and registration
2. **Network errors**: Verify connectivity
3. **Import errors**: Install dependencies
4. **Permission errors**: Check file permissions

### Getting Help
- Check logs for error messages
- Verify configuration parameters
- Test with different networks
- Consult script documentation

## 📄 Documentation

- [Scripts Documentation](scripts/README.md) - Detailed script usage
- [Technical Whitepaper](AGENT4ALL_TECHNICAL_WHITEPAPER.md) - Technical details
- [Setup Guide](SETUP_GUIDE.md) - Complete setup instructions
- [Project Summary](PROJECT_SUMMARY.md) - Cleanup and structure overview

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup
```bash
# Clone the repository
git clone https://github.com/Agents-Labs/agent4all-bittensor-subnet.git

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/

# Make your changes and submit a PR
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Bittensor Foundation](https://bittensor.com/) for the protocol
- [Agents-Labs](https://github.com/Agents-Labs) for the project
- Community contributors
- AI research community

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Agents-Labs/agent4all-bittensor-subnet&type=Date)](https://star-history.com/#Agents-Labs/agent4all-bittensor-subnet&Date)

---

**Agent4All Bittensor Subnet** - Decentralized AI for everyone, specialized for every domain.

**Repository**: [https://github.com/Agents-Labs/agent4all-bittensor-subnet](https://github.com/Agents-Labs/agent4all-bittensor-subnet)

# Agent4All Category Scripts

This directory contains specialized miners and validators for each of the 14 Agent4All categories.

## Overview

The Agent4All Bittensor subnet supports 14 different agent categories, each with specialized functionality:

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

## Directory Structure

```
scripts/
├── category_miners/          # Miner scripts for each category
│   ├── data_analyst_miner.py
│   ├── finance_miner.py
│   ├── image_miner.py
│   ├── image-to-text_miner.py
│   ├── markdown_miner.py
│   ├── planning_miner.py
│   ├── programming_miner.py
│   ├── recommendation_miner.py
│   ├── research_miner.py
│   ├── shopping_miner.py
│   ├── single_miner.py
│   ├── video_miner.py
│   ├── websearch_miner.py
│   └── wikipedia_miner.py
├── category_validators/      # Validator scripts for each category
│   ├── data_analyst_validator.py
│   ├── finance_validator.py
│   ├── image_validator.py
│   ├── image-to-text_validator.py
│   ├── markdown_validator.py
│   ├── planning_validator.py
│   ├── programming_validator.py
│   ├── recommendation_validator.py
│   ├── research_validator.py
│   ├── shopping_validator.py
│   ├── single_validator.py
│   ├── video_validator.py
│   ├── websearch_validator.py
│   └── wikipedia_validator.py
├── utils/                    # Shared utility functions
│   └── common_functions.py
├── launch_miner.py          # Launcher for miners
├── launch_validator.py      # Launcher for validators
└── README.md               # This file
```

## Usage

### Running Individual Scripts

Each script can be run directly with appropriate arguments:

#### Miner Scripts
```bash
# Run data analyst miner
python scripts/category_miners/data_analyst_miner.py \
    --wallet.name agent4all_coldkey \
    --wallet.hotkey data_analyst_hotkey \
    --subtensor.network test \
    --neuron.device cpu

# Run finance miner
python scripts/category_miners/finance_miner.py \
    --wallet.name agent4all_coldkey \
    --wallet.hotkey finance_hotkey \
    --subtensor.network test \
    --neuron.device cpu
```

#### Validator Scripts
```bash
# Run data analyst validator
python scripts/category_validators/data_analyst_validator.py \
    --wallet.name agent4all_coldkey \
    --wallet.hotkey data_analyst_validator_hotkey \
    --subtensor.network test \
    --neuron.device cpu \
    --neuron.sample_size 16

# Run finance validator
python scripts/category_validators/finance_validator.py \
    --wallet.name agent4all_coldkey \
    --wallet.hotkey finance_validator_hotkey \
    --subtensor.network test \
    --neuron.device cpu \
    --neuron.sample_size 16
```

### Using Launcher Scripts

For convenience, use the launcher scripts:

#### Launch Miners
```bash
# Launch any category miner
python scripts/launch_miner.py --category data-analyst
python scripts/launch_miner.py --category finance
python scripts/launch_miner.py --category programming

# With custom parameters
python scripts/launch_miner.py \
    --category data-analyst \
    --wallet.name my_coldkey \
    --wallet.hotkey my_hotkey \
    --subtensor.network main \
    --neuron.device gpu
```

#### Launch Validators
```bash
# Launch any category validator
python scripts/launch_validator.py --category data-analyst
python scripts/launch_validator.py --category finance
python scripts/launch_validator.py --category programming

# With custom parameters
python scripts/launch_validator.py \
    --category data-analyst \
    --wallet.name my_coldkey \
    --wallet.hotkey my_validator_hotkey \
    --subtensor.network main \
    --neuron.device gpu \
    --neuron.sample_size 32
```

## Script Features

### Common Features (All Scripts)

- **Category-specific processing**: Each script handles tasks specific to its category
- **Performance tracking**: Built-in metrics for response times and success rates
- **Error handling**: Robust error handling and logging
- **Configurable**: Command-line arguments for wallet, network, device, etc.
- **Bittensor integration**: Full integration with Bittensor protocol

### Miner Scripts

- **Task processing**: Handle category-specific tasks
- **Response generation**: Generate appropriate responses for the category
- **Performance metrics**: Track request processing times and success rates
- **Blacklist/priority**: Implement request filtering and prioritization

### Validator Scripts

- **Response evaluation**: Evaluate miner responses using category-specific criteria
- **Score calculation**: Calculate weighted scores based on multiple metrics
- **Score distribution**: Track score distributions and statistics
- **Network sampling**: Sample miners from the network for evaluation

## Configuration

### Default Parameters

All scripts use these default parameters:
- `--wallet.name`: "agent4all_coldkey"
- `--wallet.hotkey`: "{category}_hotkey" (miners) or "{category}_validator_hotkey" (validators)
- `--subtensor.network`: "test"
- `--neuron.device`: "cpu"
- `--neuron.sample_size`: 16 (validators only)
- `--logging.level`: "INFO"

### Networks

- **test**: Testnet (default)
- **main**: Mainnet
- **local**: Local network

### Devices

- **cpu**: CPU processing (default)
- **cuda**: GPU processing (if available)
- **mps**: Apple Silicon GPU (if available)

## Category-Specific Features

### Data Analyst
- Data analysis and visualization tasks
- Statistical analysis and modeling
- Performance metrics: accuracy, data quality, insight quality

### Finance
- Financial analysis and investment advice
- Risk assessment and portfolio optimization
- Performance metrics: profitability, risk assessment, accuracy

### Image
- Image generation and processing
- Style transfer and enhancement
- Performance metrics: quality, relevance, creativity

### Image-to-Text
- Image captioning and OCR
- Visual question answering
- Performance metrics: accuracy, fluency, completeness

### Markdown
- Markdown processing and documentation
- Content formatting and conversion
- Performance metrics: readability, structure, completeness

### Planning
- Project planning and scheduling
- Timeline creation and resource allocation
- Performance metrics: feasibility, completeness, efficiency

### Programming
- Code generation and review
- Debugging and optimization
- Performance metrics: correctness, efficiency, readability

### Recommendation
- Product and content recommendation
- Collaborative filtering
- Performance metrics: precision, recall, user satisfaction

### Research
- Research and information gathering
- Academic and web research
- Performance metrics: relevance, accuracy, completeness

### Shopping
- E-commerce and shopping assistance
- Product search and price comparison
- Performance metrics: relevance, price accuracy, user satisfaction

### Single
- General purpose conversation
- Question answering and assistance
- Performance metrics: helpfulness, accuracy, engagement

### Video
- Video processing and analysis
- Video generation and enhancement
- Performance metrics: quality, accuracy, processing speed

### Websearch
- Web search and browsing
- Content extraction and news gathering
- Performance metrics: relevance, accuracy, freshness

### Wikipedia
- Wikipedia content processing
- Content summarization and citation finding
- Performance metrics: accuracy, completeness, citation

## Development

### Adding New Categories

To add a new category:

1. Update `category_registry.py` with the new category
2. Create miner script: `scripts/category_miners/{category}_miner.py`
3. Create validator script: `scripts/category_validators/{category}_validator.py`
4. Update `scripts/utils/common_functions.py` with category-specific configuration
5. Test the new scripts

### Customizing Scripts

Each script can be customized by:

1. **Modifying task handlers**: Override the `handle_{category}_task` method in miners
2. **Customizing evaluation**: Override evaluation methods in validators
3. **Adding metrics**: Extend the performance tracking system
4. **Configuring weights**: Adjust scoring weights in the evaluation engine

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Wallet errors**: Check wallet configuration and balance
3. **Network errors**: Verify network connectivity and configuration
4. **Permission errors**: Ensure scripts have execute permissions

### Logging

All scripts support configurable logging levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

### Performance Monitoring

Monitor script performance using:
- Built-in metrics in each script
- Bittensor network statistics
- System resource monitoring

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify configuration parameters
3. Test with different networks/devices
4. Consult the main project documentation

## License

These scripts are part of the Agent4All Bittensor subnet project and follow the same license terms. 
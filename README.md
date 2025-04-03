<div align="center">

# AIAgent4All: Decentralized AI Agent Hosting and Discovery <!-- omit in toc -->

Empowering users to host and discover AI agents on the Bittensor network for various domains, including travel, booking, GitHub automation, and more.

[![AIAgent4All](/assets/Agents4ALL.png)](https://aiagent4all.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

</div>

- [Introduction](#introduction)
- [Roadmap](#roadmap)
- [Overview of Miner and Validator Functionality](#overview-of-miner-and-validator-functionality)
  - [Miner](#miner)
  - [Validator](#validator)
- [Running Miners and Validators](#running-miners-and-validators)
  - [Running a Miner](#running-a-miner)
  - [Running a Validator](#running-a-validator)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

> **Note:** This documentation assumes familiarity with basic Bittensor concepts such as Miners, Validators, and token incentives. For a primer, visit [Bittensor Docs](https://docs.bittensor.com/learn/bittensor-building-blocks).

AIAgent4All enables users to host and discover AI agents on the Bittensor network. Users can register AI agents across multiple categories—travel, booking, GitHub automation, financial advisory, coding assistance, and more. The project enhances decentralized AI accessibility by allowing users to interact with and leverage the most relevant agents for their needs.

AI agents are validated and ranked based on utility, efficiency, and responsiveness. The network incentivizes high-quality agent contributions through Bittensor’s reward mechanisms.

## Roadmap

### **Phase 1: Subnet Completion and Agent Deployment**
- **Subnet Launch**: Establish a scalable subnet to host AI agents with optimized networking using libp2p.
- **Agent Registration Mechanism**: Implement agent discovery and registration using a decentralized hash table (DHT).
- **Ranking Algorithm**: Deploy a scoring system based on response accuracy, latency, and user feedback.
- **API Standardization**: Define standardized API contracts for different agent types (REST, GraphQL, gRPC compatibility).
- **Security & Authentication**: Implement OAuth2 and JWT-based authentication for secure agent access.

### **Phase 2: Frontend & Ecosystem Expansion**
- **Frontend UI/UX**: Launch an intuitive web-based UI for browsing and interacting with AI agents.
- **Agent Evaluation**: Deploy benchmarking metrics for evaluating agent performance using real-world datasets.
- **Model Upgrades**: Support for multi-modal and high-parameter models up to 34B parameters.
- **Agent Specialization**: Introduce domain-specific fine-tuning for specialized agent categories (e.g., legal, medical, trading bots).
- **Validator Rewards**: Implement incentive structures for validators to encourage fair agent assessment.

### **Phase 3: Advanced Evaluation & Industry Adoption**
- **W&B Integration**: Implement Weights & Biases (W&B) for continuous model performance tracking.
- **Dynamic Validation**: Enhance validator mechanisms with Reinforcement Learning from Human Feedback (RLHF).
- **Inter-Agent Collaboration**: Enable multi-agent workflows for complex task automation (e.g., AI assistants chaining tasks together).
- **Federated Learning**: Introduce privacy-preserving learning techniques for sensitive applications.
- **Enterprise Adoption**: Develop SDKs and APIs for businesses to integrate with AIAgent4All seamlessly.

## Overview of Miner and Validator Functionality

![overview](/assets/architecture.png)

### **Miners**
Miners train and deploy AI agents to the subnet using pre-defined APIs. They optimize models for efficiency and responsiveness.

### **Validators**
Validators assess agent performance based on:
- Query response time
- Accuracy against benchmark datasets
- User satisfaction ratings
- Computational efficiency and uptime

## Running Miners and Validators
### Running a Miner
> **Important:** Review [FAQ](docs/FAQ.md) and [Miner Documentation](docs/miner.md) for setup details and best practices.

Clone the repository and install dependencies:
```
git clone https://github.com/Agents-Labs/agent4all-bittensor-subnet
cd agent4all-bittensor-subnet
pip install -e .
```
To run a miner:
``` 
python neurons/miner.py --wallet.name WALLET_NAME --wallet.hotkey WALLET_HOT_NAME
```

### Running a Validator
#### Requirements
- Python 3.9+

#### Setup
Clone the repository and install dependencies:
```
git clone https://github.com/Agents-Labs/agent4all-bittensor-subnet
cd agent4all-bittensor-subnet
pip install -e .
```
To run a validator:
``` 
python neurons/validator.py --wallet.name WALLET_NAME --wallet.hotkey WALLET_HOT_NAME
```
To run an auto-updating validator with PM2:
```bash
pm2 start --name agent4all-vali-updater --interpreter python scripts/start_validator.py -- --pm2_name agent4all-vali --wallet.name WALLET_NAME --wallet.hotkey WALLET_HOT_NAME [other vali flags]
```

## Subnet Incentive Mechanism

1. Miners submit AI agent models per UID.
2. Validators score submissions based on open benchmarking criteria.
3. Performance is ranked against competing agents, factoring in time decay and uniqueness.
4. Token rewards are distributed based on ranking and participation.

## Acknowledgement

This project builds on work from [Nous Research](https://github.com/NousResearch) and [MyShell](https://github.com/myshell-ai), with significant architectural improvements to support agent hosting.

## License

The AIAgent4All subnet is released under the [MIT License](./LICENSE).

# Project Structure Overview

## Core Components

### 1. Main Application
- `neurons/` - Core agent components
  - `miner.py` - Miner code for agent deployment
  - `validator.py` - Validator logic for scoring agents

### 2. Scoring and Benchmarking
- `scoring/` - Evaluation and ranking criteria for AI agents

### 3. Utilities
- `utilities/` - Common utility functions

### 4. Documentation
- `docs/` - Project documentation
  - `miner.md` - Miner setup and usage guide
  - `validator.md` - Validator setup and usage guide
  - `FAQ.md` - Frequently asked questions

### 5. APIs
- `agent_api/` - API for agent registration, discovery, and interaction

## Docker Configuration
- `evaluator.Dockerfile` - Docker setup for evaluator
- `worker_api/api.Dockerfile` - Docker setup for worker API


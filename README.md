<div align="center">

# AIAgent4All: Decentralized AI Agent Hosting and Discovery <!-- omit in toc -->

Empowering users to host and discover AI agents on the Bittensor network for various domains, including travel, booking, GitHub automation, and more.

![AIAgent4All](/assets/Agents4ALL.png)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

</div>

- [Introduction](#introduction)
- [Roadmap](#roadmap)
- [Overview of Miner and Validator Functionality](#overview-of-miner-and-validator-functionality)
  - [Miner](#miner)snappymc
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


## AI Agents with Different Processes

### Sequential Process

The simplest form of task execution where tasks are performed one after another.

```mermaid
graph LR
    Input[Input] --> A1
    subgraph Agents
        direction LR
        A1[Agent 1] --> A2[Agent 2] --> A3[Agent 3]
    end
    A3 --> Output[Output]

    classDef input fill:#8B0000,stroke:#7C90A0,color:#fff
    classDef process fill:#189AB4,stroke:#7C90A0,color:#fff
    classDef transparent fill:none,stroke:none

    class Input,Output input
    class A1,A2,A3 process
    class Agents transparent
```

### Hierarchical Process

Uses a manager agent to coordinate task execution and agent assignments.

```mermaid
graph TB
    Input[Input] --> Manager
    
    subgraph Agents
        Manager[Manager Agent]
        
        subgraph Workers
            direction LR
            W1[Worker 1]
            W2[Worker 2]
            W3[Worker 3]
        end
        
        Manager --> W1
        Manager --> W2
        Manager --> W3
    end
    
    W1 --> Manager
    W2 --> Manager
    W3 --> Manager
    Manager --> Output[Output]

    classDef input fill:#8B0000,stroke:#7C90A0,color:#fff
    classDef process fill:#189AB4,stroke:#7C90A0,color:#fff
    classDef transparent fill:none,stroke:none

    class Input,Output input
    class Manager,W1,W2,W3 process
    class Agents,Workers transparent
```

### Workflow Process

Advanced process type supporting complex task relationships and conditional execution.

```mermaid
graph LR
    Input[Input] --> Start
    
    subgraph Workflow
        direction LR
        Start[Start] --> C1{Condition}
        C1 --> |Yes| A1[Agent 1]
        C1 --> |No| A2[Agent 2]
        A1 --> Join
        A2 --> Join
        Join --> A3[Agent 3]
    end
    
    A3 --> Output[Output]

    classDef input fill:#8B0000,stroke:#7C90A0,color:#fff
    classDef process fill:#189AB4,stroke:#7C90A0,color:#fff
    classDef decision fill:#2E8B57,stroke:#7C90A0,color:#fff
    classDef transparent fill:none,stroke:none

    class Input,Output input
    class Start,A1,A2,A3,Join process
    class C1 decision
    class Workflow transparent
```

#### Agentic Routing Workflow

Create AI agents that can dynamically route tasks to specialized LLM instances.

```mermaid
flowchart LR
    In[In] --> Router[LLM Call Router]
    Router --> LLM1[LLM Call 1]
    Router --> LLM2[LLM Call 2]
    Router --> LLM3[LLM Call 3]
    LLM1 --> Out[Out]
    LLM2 --> Out
    LLM3 --> Out
    
    style In fill:#8B0000,color:#fff
    style Router fill:#2E8B57,color:#fff
    style LLM1 fill:#2E8B57,color:#fff
    style LLM2 fill:#2E8B57,color:#fff
    style LLM3 fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
```

#### Agentic Orchestrator Worker

Create AI agents that orchestrate and distribute tasks among specialized workers.

```mermaid
flowchart LR
    In[In] --> Router[LLM Call Router]
    Router --> LLM1[LLM Call 1]
    Router --> LLM2[LLM Call 2]
    Router --> LLM3[LLM Call 3]
    LLM1 --> Synthesizer[Synthesizer]
    LLM2 --> Synthesizer
    LLM3 --> Synthesizer
    Synthesizer --> Out[Out]
    
    style In fill:#8B0000,color:#fff
    style Router fill:#2E8B57,color:#fff
    style LLM1 fill:#2E8B57,color:#fff
    style LLM2 fill:#2E8B57,color:#fff
    style LLM3 fill:#2E8B57,color:#fff
    style Synthesizer fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
```

#### Agentic Autonomous Workflow

Create AI agents that can autonomously monitor, act, and adapt based on environment feedback.

```mermaid
flowchart LR
    Human[Human] <--> LLM[LLM Call]
    LLM -->|ACTION| Environment[Environment]
    Environment -->|FEEDBACK| LLM
    LLM --> Stop[Stop]
    
    style Human fill:#8B0000,color:#fff
    style LLM fill:#2E8B57,color:#fff
    style Environment fill:#8B0000,color:#fff
    style Stop fill:#333,color:#fff
```

#### Agentic Parallelization

Create AI agents that can execute tasks in parallel for improved performance.

```mermaid
flowchart LR
    In[In] --> LLM2[LLM Call 2]
    In --> LLM1[LLM Call 1]
    In --> LLM3[LLM Call 3]
    LLM1 --> Aggregator[Aggregator]
    LLM2 --> Aggregator
    LLM3 --> Aggregator
    Aggregator --> Out[Out]
    
    style In fill:#8B0000,color:#fff
    style LLM1 fill:#2E8B57,color:#fff
    style LLM2 fill:#2E8B57,color:#fff
    style LLM3 fill:#2E8B57,color:#fff
    style Aggregator fill:#fff,color:#000
    style Out fill:#8B0000,color:#fff
```

#### Agentic Prompt Chaining

Create AI agents with sequential prompt chaining for complex workflows.

```mermaid
flowchart LR
    In[In] --> LLM1[LLM Call 1] --> Gate{Gate}
    Gate -->|Pass| LLM2[LLM Call 2] -->|Output 2| LLM3[LLM Call 3] --> Out[Out]
    Gate -->|Fail| Exit[Exit]
    
    style In fill:#8B0000,color:#fff
    style LLM1 fill:#2E8B57,color:#fff
    style LLM2 fill:#2E8B57,color:#fff
    style LLM3 fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
    style Exit fill:#8B0000,color:#fff
```

#### Agentic Evaluator Optimizer

Create AI agents that can generate and optimize solutions through iterative feedback.

```mermaid
flowchart LR
    In[In] --> Generator[LLM Call Generator] 
    Generator -->|SOLUTION| Evaluator[LLM Call Evaluator] -->|ACCEPTED| Out[Out]
    Evaluator -->|REJECTED + FEEDBACK| Generator
    
    style In fill:#8B0000,color:#fff
    style Generator fill:#2E8B57,color:#fff
    style Evaluator fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
```

#### Repetitive Agents

Create AI agents that can efficiently handle repetitive tasks through automated loops.

```mermaid
flowchart LR
    In[Input] --> LoopAgent[("Looping Agent")]
    LoopAgent --> Task[Task]
    Task --> |Next iteration| LoopAgent
    Task --> |Done| Out[Output]
    
    style In fill:#8B0000,color:#fff
    style LoopAgent fill:#2E8B57,color:#fff,shape:circle
    style Task fill:#2E8B57,color:#fff
    style Out fill:#8B0000,color:#fff
```

## Overview of Miner and Validator Functionality

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

![AIAgent4All](/assets/aiagent.png)
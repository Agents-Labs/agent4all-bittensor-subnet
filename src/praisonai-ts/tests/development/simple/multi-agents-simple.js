const { Agent, Agent4ALLAgents } = require('agent4all');

const researchAgent = new Agent({ instructions: 'Research about AI' });
const summariseAgent = new Agent({ instructions: 'Summarise research agent\'s findings' });

const agents = new Agent4ALLAgents({ agents: [researchAgent, summariseAgent] });
agents.start();

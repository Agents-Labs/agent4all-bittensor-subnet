// Export implementation based on mode
let useTaskMode = false;

export function setTaskMode(enabled: boolean) {
  useTaskMode = enabled;
}

export { Agent, Agent4ALLAgents, Task } from './proxy';
export type { ProxyAgentConfig } from './proxy';
export type { AgentConfig } from './types';
export type { TaskConfig } from './types';
export type { Agent4ALLAgentsConfig, SimpleAgentConfig } from './simple';

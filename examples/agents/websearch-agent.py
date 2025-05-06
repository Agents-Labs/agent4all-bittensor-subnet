# Import necessary classes from the praisonaiagents package
from praisonaiagents import Agent, Tools
from praisonaiagents.tools import duckduckgo

# Create an instance of the Agent class with specific instructions
# In this case, the agent is instructed to act as a Web Search Agent
agent = Agent(instructions="You are a Web Search Agent", tools=[duckduckgo])

# Start the agent's operation with a specific search query
# The agent will search for information about "AI 2024"
agent.start("Search about AI 2024")

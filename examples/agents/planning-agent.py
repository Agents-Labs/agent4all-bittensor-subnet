# Importing required classes from the praisonaiagents module
from praisonaiagents import Agent, Tools  # Importing Agent and Tools classes
from praisonaiagents.tools import duckduckgo  # Importing the DuckDuckGo search tool

# Creating an instance of the Agent class with specific instructions
# The instruction specifies that this agent is a Planning Agent
agent = Agent(instructions="You are a Planning Agent", tools=[duckduckgo])

# Starting the agent with a specific query to plan a trip
# The input string indicates the user is looking for a hotel and flight to London next week
agent.start("I want to go London next week, find me a good hotel and flight")

# Importing the necessary classes and tools from the praisonaiagents library
from praisonaiagents import Agent, Tools
from praisonaiagents.tools import duckduckgo

# Creating an instance of the Agent class, which is configured to act as a shopping assistant
# The instructions specify the role of the agent, and tools specify the tools it can use
agent = Agent(instructions="You are a Shopping Agent", tools=[duckduckgo])

# Starting the agent with a specific task: to find prices for the iPhone 16 Pro Max 
# by checking 5 different stores and returning the information in a tabular format
agent.start("I want to buy iPhone 16 Pro Max, check 5 stores and give me price in table")

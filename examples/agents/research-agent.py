# Import the necessary classes and tools from the praisonaiagents library
from praisonaiagents import Agent, Tools
from praisonaiagents.tools import duckduckgo  # Import the DuckDuckGo tool for web searching

# Create an instance of the Agent class with specified instructions and tools
agent = Agent(instructions="You are a Research Agent", tools=[duckduckgo])

# Start the agent with the task of researching information about AI in the year 2024
agent.start("Research about AI 2024")

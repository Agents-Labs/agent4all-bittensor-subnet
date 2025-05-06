# Import necessary classes and functions from the praisonaiagents library
from praisonaiagents import AutoAgents
from praisonaiagents.tools import duckduckgo  # Import the DuckDuckGo search tool

# Initialize AutoAgents with specific instructions and configurations
agents = AutoAgents(
    instructions="Search for information about AI Agents",  # Instructions for the agent on what to do
    tools=[duckduckgo],                                   # List of tools to be used by the agents (in this case, DuckDuckGo for searching)
    process="sequential",                                 # Specify that tasks should be processed in a sequential manner
    verbose=True                                          # Enable verbose output for detailed logging of the operations
)

# Start the execution of the agents based on the provided instructions
agents.start()

# Import the necessary modules from the praisonaiagents library
from praisonaiagents import Agent, Tools
from praisonaiagents.tools import get_stock_price, get_stock_info, get_historical_data

# Initialize an Agent with specific instructions and tools for stock research
agent = Agent(
    instructions="You are a Research Agent",  # Instructions for the agent's role
    tools=[get_stock_price, get_stock_info, get_historical_data]  # List of tools the agent can use
)

# Start the agent with a specific task related to stock analysis
agent.start("Understand current stock price and historical data of Apple and Google. Tell me if I can invest in them")

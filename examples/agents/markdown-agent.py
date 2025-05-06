# Import the Agent class from the praisonaiagents module
from praisonaiagents import Agent

# Create an instance of the Agent class with specific instructions 
# directing the agent to output content in Markdown format
agent = Agent(instructions="You are a Markdown Agent, output in markdown format")

# Start the agent with a prompt to write a blog post about AI
# This method call initiates the agent's processing with the provided instructions
agent.start("Write a blog post about AI")

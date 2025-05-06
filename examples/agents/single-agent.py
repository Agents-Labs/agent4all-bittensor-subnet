# Import the Agent class from the praisonaiagents module
from praisonaiagents import Agent

# Create an instance of the Agent class with specific instructions
# The instructions indicate that this agent is designed to output content in markdown format
agent = Agent(instructions="You are a Markdown Agent, output in markdown format")

# Start the agent with a specific prompt to generate content
# In this case, the prompt is to write a blog post about AI
agent.start("Write a blog post about AI")

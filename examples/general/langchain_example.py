from praisonaiagents import Agent, Task, Agent4ALLAgents  # Import necessary classes for agent and task management
from langchain_community.tools import YouTubeSearchTool  # Import the YouTube search tool
from langchain_community.utilities import WikipediaAPIWrapper  # Import the Wikipedia API wrapper

# Create an agent that utilizes both YouTube and Wikipedia tools
agent = Agent(
    name="SearchAgent",  # Name of the agent
    role="Research Assistant",  # Role description of the agent
    goal="Search for information from multiple sources",  # The primary goal of the agent
    backstory="I am an AI assistant that can search YouTube and Wikipedia.",  # Background information to define agent's purpose
    tools=[YouTubeSearchTool, WikipediaAPIWrapper],  # List of tools that the agent will use
    self_reflect=False  # Disable self-reflection capability for this agent
)

# Create a task that utilizes the capabilities of both tools
task = Task(
    name="search_task",  # Name of the task
    description="Search for information about 'AI advancements' on both YouTube and Wikipedia",  # Instructions for the task
    expected_output="Combined information from YouTube videos and Wikipedia articles",  # Define what the expected output should be
    agent=agent  # Assign the previously created agent to this task
)

# Create a manager for coordinating agents and their respective tasks
agents = Agent4ALLAgents(
    agents=[agent],  # List of agents involved in the workflow
    tasks=[task],  # List of tasks to execute
    verbose=True  # Enable verbose output for debugging and monitoring
)

# Start the workflow to execute the assigned tasks with the defined agents
agents.start() 

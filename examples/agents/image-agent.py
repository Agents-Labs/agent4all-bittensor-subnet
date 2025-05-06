# Import necessary libraries and components
from praisonaiagents import Agent, Tools
from praisonaiagents.tools import duckduckgo

# Initialize an Agent with specific instructions and tools for information retrieval
agent = Agent(instructions="You are an Image Analysis Agent", tools=[duckduckgo])
# Start the agent with a query about finding a hotel and flight to London
agent.start("I want to go London next week, find me a good hotel and flight")

# Import additional components for creating tasks and managing agents
from praisonaiagents import Agent, Task, Agent4ALLAgents

# Create an instance of an Image Analysis Agent
image_agent = Agent(
    name="ImageAnalyst",  # Name of the agent
    role="Image Analysis Specialist",  # Role description of the agent
    goal="Analyze images and videos to extract meaningful information",  # Goal for the agent
    backstory="""You are an expert in computer vision and image analysis.
    You excel at describing images, detecting objects, and understanding visual content.""",  # Background story for the agent
    llm="gpt-4o-mini",  # Specify the language model to be used
    self_reflect=False  # Flag indicating whether the agent should self-reflect
)

# 1. Define a task for analyzing a famous landmark from a specified image URL
task1 = Task(
    name="analyze_landmark",  # Unique name for the task
    description="Describe this famous landmark and its architectural features.",  # Description of the task
    expected_output="Detailed description of the landmark's architecture and significance",  # Expected outcome of the task
    agent=image_agent,  # Assign the image agent to this task
    images=["https://upload.wikimedia.org/wikipedia/commons/b/bf/Krakow_-_Kosciol_Mariacki.jpg"]  # URL of the image to analyze
)

# 2. Define a task for analyzing a local image file
task2 = Task(
    name="analyze_local_image",  # Unique name for the task
    description="What objects can you see in this image? Describe their arrangement.",  # Description of the task
    expected_output="Detailed description of objects and their spatial relationships",  # Expected outcome of the task
    agent=image_agent,  # Assign the image agent to this task
    images=["image.jpg"]  # Local file path of the image to analyze
)

# Create a Agent4ALLAgents instance to manage the created agents and tasks
agents = Agent4ALLAgents(
    agents=[image_agent],  # List of agents to be managed
    tasks=[task1, task2],  # List of tasks to be executed
    process="sequential",  # Define the processing order of tasks
    verbose=1  # Set verbosity level for logging output
)

# Execute all defined tasks using the agents
agents.start()  # Start the execution of all tasks in the agent management system

# Import necessary classes from the praisonaiagents library
from praisonaiagents import Agent, Tools
from praisonaiagents.tools import duckduckgo

# Create an instance of the Agent responsible for finding travel information
agent = Agent(instructions="You are a Image Analysis Agent", tools=[duckduckgo])

# Start the agent with a specific query about travel to London
agent.start("I want to go London next week, find me a good hotel and flight")

# Import more classes needed for creating tasks and managing agents
from praisonaiagents import Agent, Task, Agent4ALLAgents

# Create an Image Analysis Agent with specific attributes
image_agent = Agent(
    name="ImageAnalyst",  # Name of the agent
    role="Image Analysis Specialist",  # Role description of the agent
    goal="Analyze images and videos to extract meaningful information",  # Goal of the agent
    backstory="""You are an expert in computer vision and image analysis.
    You excel at describing images, detecting objects, and understanding visual content.""",  # Backstory to define agent's persona
    llm="gpt-4o-mini",  # Specify the language model to use
    self_reflect=False  # Indicate not to enable self-reflection
)

# 1. Define a Task that involves analyzing a famous landmark
task1 = Task(
    name="analyze_landmark",  # Name of the task
    description="Describe this famous landmark and its architectural features.",  # Description of what the task involves
    expected_output="Detailed description of the landmark's architecture and significance",  # Expected outcome
    agent=image_agent,  # Assign the task to the image agent created earlier
    images=["https://upload.wikimedia.org/wikipedia/commons/b/bf/Krakow_-_Kosciol_Mariacki.jpg"]  # URL of the image to be analyzed
)

# 2. Define another Task that involves analyzing a local image file
task2 = Task(
    name="analyze_local_image",  # Name of the task
    description="What objects can you see in this image? Describe their arrangement.",  # Description of the task
    expected_output="Detailed description of objects and their spatial relationships",  # Expected outcome
    agent=image_agent,  # Assign to the same image agent
    images=["image.jpg"]  # The path to the local image file to be analyzed
)

# Create an instance of Agent4ALLAgents to manage multiple agents and tasks
agents = Agent4ALLAgents(
    agents=[image_agent],  # List of agents to be managed
    tasks=[task1, task2],  # List of tasks to be executed
    process="sequential",  # Specify that tasks should be processed sequentially
    verbose=1  # Set verbosity level for logging output
)

# Start the agents and run all defined tasks
agents.start()

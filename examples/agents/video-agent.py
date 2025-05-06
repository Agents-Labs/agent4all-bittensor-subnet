# Import necessary classes from the praisonaiagents library
from praisonaiagents import Agent, Task, Agent4ALLAgents

# Create a Video Analysis Agent
video_agent = Agent(
    name="VideoAnalyst",  # Name of the agent
    role="Video Analysis Specialist",  # Role of the agent
    goal="Analyze images and videos to extract meaningful information",  # Main objective of the agent
    backstory="""You are an expert in computer vision and image analysis.
    You excel at describing images, detecting objects, and understanding visual content.""",  # Background to give context to the agent's capabilities
    llm="gpt-4o-mini",  # Specify the language model used for the agent
    self_reflect=False  # Indicates whether the agent can reflect on its own thought process
)

# Define a task that the Video Analysis Agent will perform
task1 = Task(
    name="analyze_video",  # Name of the task
    description="""Watch this video and provide:
    1. A summary of the main events  # Ask for a summary of key events in the video
    2. Key objects and people visible  # Identification of important objects and people in the video
    3. Any text or important information shown  # Extraction of any notable text or details presented in the video
    4. The overall context and setting""",  # Request for context and setting for better understanding
    expected_output="Comprehensive analysis of the video content",  # Expected results from the task
    agent=video_agent,  # Connect the task with the video analysis agent created above
    images=["video.mp4"]  # Specify the video file to be analyzed
)

# Create an instance of Agent4ALLAgents to manage the agents and tasks
agents = Agent4ALLAgents(
    agents=[video_agent],  # List of agents involved in the analysis
    tasks=[task1],  # List of tasks assigned to the agents
    process="sequential",  # Define the process as sequential execution
    verbose=1  # Set verbosity level for logging output during execution
)

# Start executing the tasks assigned to the agents
agents.start()

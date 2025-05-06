# Import necessary classes from the praisonaiagents library
from praisonaiagents import Agent, Task, Agent4ALLAgents
import logging
import os

# Configure logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)  # Create a logger instance for this module

# Define the configuration for the Knowledge instance
config = {
    "vector_store": {
        "provider": "chroma",  # Use the Chroma vector store as the backend
        "config": {
            "collection_name": "knowledge_test",  # Specify the collection name in the vector store
            "path": ".praison",  # Define the path for storing the vector data
        }
    }
}

# Create an agent with knowledge capabilities
knowledge_agent = Agent(
    name="KnowledgeAgent",  # The name of the agent
    role="Information Specialist",  # The role or function of the agent
    goal="Store and retrieve knowledge efficiently",  # The main objective of the agent
    backstory="Expert in managing and utilizing stored knowledge",  # Background information about the agent
    knowledge=["sample.pdf"],  # A list of initial knowledge documents the agent has access to
    knowledge_config=config,  # The knowledge configuration defined above
    verbose=True  # Enable verbose output for more detailed logging during execution
)

# Define a task for the agent
knowledge_task = Task(
    name="knowledge_task",  # The name of the task
    description="Who is Mervin Praison?",  # A detailed description of what the task entails
    expected_output="Answer to the question",  # The expected output format for the task
    agent=knowledge_agent  # The agent responsible for executing this task
)

# Create and start the agent and task processing
agents = Agent4ALLAgents(
    agents=[knowledge_agent],  # List of agents to be used in this process
    tasks=[knowledge_task],  # List of tasks to be assigned to the agents
    process="sequential",  # Specify the processing order ("sequential" or "parallel")
    user_id="user1"  # Identifier for the user initiating the process
)

# Start execution of the agents and tasks
result = agents.start()  # Execute the defined agents and tasks, storing the result

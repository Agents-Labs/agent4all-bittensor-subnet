# Import necessary modules from the praisonaiagents package
from praisonaiagents import Agent, Task, Agent4ALLAgents

# Define the configuration for the Knowledge instance
# This configuration specifies the vector store settings, including the provider 
# and the parameters for the collection where data will be stored/retrieved.
config = {
    "vector_store": {
        "provider": "chroma",  # Specify the provider for the vector database
        "config": {
            "collection_name": "praison",  # Name of the collection in the vector store
            "path": ".praison"  # Path where the vector data will be stored
        }
    }
}

# Create an agent instance
rag_agent = Agent(
    name="RAG Agent",  # The name of the agent
    role="Information Specialist",  # The role or purpose of the agent
    goal="Retrieve knowledge efficiently",  # The primary goal of the agent
    llm="gpt-4o-mini"  # The language model the agent uses for processing
)

# Define a task for the agent
rag_task = Task(
    name="RAG Task",  # The name of the task
    description="What is KAG?",  # A brief description of what the task involves
    expected_output="Answer to the question",  # What output is expected from the task
    agent=rag_agent,  # Associate the defined agent with this task
    context=[config]  # Provide the vector database configuration as context for the task
)

# Build the agents management system
agents = Agent4ALLAgents(
    agents=[rag_agent],  # Add the previously created agent to the agents list
    tasks=[rag_task],  # Add the previously defined task to the tasks list
    user_id="user1"  # Assign a user ID to this instance of agents
)

# Start the agents management system to execute the defined tasks
agents.start()

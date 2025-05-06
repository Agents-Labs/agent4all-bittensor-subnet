# Import the Agent class from the praisonaiagents module
from praisonaiagents import Agent

# Configuration for the vector store which will store the knowledge vectors
config = {
    "vector_store": {
        "provider": "chroma",  # The chosen provider for the vector store
        "config": {
            "collection_name": "praison",  # Name of the collection to be used in the vector store
            "path": ".praison",              # Path where the vector store data will be saved
        }
    }
}

# Instantiate the Agent with a name, instructions, and knowledge configuration
agent = Agent(
    name="Knowledge Agent",  # Name given to the agent
    instructions="You answer questions based on the provided knowledge.",  # Instructions on how the agent should behave
    knowledge=["small.pdf"],  # List of knowledge sources, in this case a PDF file
    knowledge_config=config  # Configuration for the knowledge storage
)

# Start the agent with a query to answer
agent.start("What is KAG in one line?")  # Sample question to the agent

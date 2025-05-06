from praisonaiagents import Agent, Task, Agent4ALLAgents

# Define the configuration for the Knowledge instance
config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "praison",
            "path": ".praison"
        }
    }
}

# Create an agent
rag_agent = Agent(
    name="RAG Agent",
    role="Information Specialist",
    goal="Retrieve knowledge efficiently",
    llm="gpt-4o-mini"
)

# Define a task for the agent
rag_task = Task(
    name="RAG Task",
    description="What is KAG?",
    expected_output="Answer to the question",
    agent=rag_agent,
    context=[config] # Vector Database provided as context
)

# Build Agents
agents = Agent4ALLAgents(
    agents=[rag_agent],
    tasks=[rag_task],
    user_id="user1"
)

# Start Agents
agents.start()
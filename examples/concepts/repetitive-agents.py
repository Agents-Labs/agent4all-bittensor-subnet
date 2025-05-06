# Import necessary modules from the praisonaiagents package
from praisonaiagents import Agent, Task, Agent4ALLAgents

# Create an agent instance that will generate a loop of tasks
agent = Agent(
    instructions="You are a loop agent that creates a loop of tasks.",  # Instructions defining the agent's role
    llm="gpt-4o-mini"  # Specify the language model used by the agent
)

# Define a task for the agent to perform
task = Task(
    description="Create the list of tasks to be looped through.",  # Description of the task's purpose
    agent=agent,  # Associate this task with the defined agent
    task_type="loop",  # Task type set to loop indicating it will generate or handle repetitive tasks
    input_file="tasks.csv"  # Input file that contains the tasks to be looped through
)

# Create an instance of the Agent4ALLAgents management system
agents = Agent4ALLAgents(
    agents=[agent],  # List of agents to include, in this case only one agent
    tasks=[task],  # List of tasks to include, in this case only one task
    process="workflow",  # Define the overall process type, here it is set to 'workflow'
    max_iter=30  # Set the maximum number of iterations for the loop
)

# Start the agents management system to execute the defined tasks and workflow
agents.start()

# Import necessary classes from the praisonaiagents module
from praisonaiagents import Agent, Task, Agent4ALLAgents

# Create a generator agent
generator = Agent(
    name="Generator",  # Name of the agent
    role="Solution generator",  # Role of the agent in the workflow
    goal="Generate initial solutions and incorporate feedback",  # Goal of the agent
    instructions=(  # Instructions for the agent on how to perform its task
        "1. Look at the context from previous tasks.\n"  # Step 1: Review prior context
        "2. If you see that you have already produced 2 points, then add another 2 new points "
        "   so that the total becomes 10.\n"  # Step 2: Check and add points if necessary
        "3. Otherwise, just produce the first 2 points.\n"  # Step 3: Produce points if not enough
        "4. Return only the final list of points, with no extra explanation."  # Step 4: Output format
    )
)

# Create an evaluator agent
evaluator = Agent(
    name="Evaluator",  # Name of the agent
    role="Solution evaluator",  # Role of the agent in the workflow
    goal="Evaluate solutions and provide improvement feedback",  # Goal of the agent
    instructions=(  # Instructions for the agent on how to perform its evaluation task
        "1. Count how many lines in the response start with a number and a period (like '1. ' or '2. ').\n"  # Step 1: Counting the points
        "2. If there are 10 or more, respond with 'done'.\n"  # Step 2: Determine if the count is sufficient
        "3. Otherwise, respond with 'more'.\n"  # Step 3: If not enough points, request more
        "4. Return only the single word: 'done' or 'more'."  # Step 4: Output format for evaluation
    )
)

# Create tasks for the feedback loop
generate_task = Task(
    name="generate",  # Name of the task
    description="Write 2 points about AI including if anything exciting from previous points",  # Description of the task
    expected_output="2 points",  # Expected output format
    agent=generator,  # Agent responsible for this task
    is_start=True,  # This task is the starting point of the workflow
    task_type="decision",  # Type of task
    next_tasks=["evaluate"]  # Next task to be executed after generating points
)

evaluate_task = Task(
    name="evaluate",  # Name of the task
    description="Check if there are 10 points about AI",  # Description of the task
    expected_output="more or done",  # Expected output format
    agent=evaluator,  # Agent responsible for this task
    next_tasks=["generate"],  # Next task to execute after evaluation
    context=[generate_task],  # Previous task context for the evaluator
    task_type="decision",  # Type of task
    condition={  # Conditions for transitioning between tasks
        "more": ["generate"],  # If more points are needed, return to generation
        "done": [""]  # If sufficient points, exit the workflow
    }
)

# Create a workflow manager with the defined agents and tasks
workflow = Agent4ALLAgents(
    agents=[generator, evaluator],  # List of agents involved in the workflow
    tasks=[generate_task, evaluate_task],  # List of tasks to be executed
    process="workflow",  # Type of process being managed
    verbose=True  # Enable verbose output for debugging purposes
)

# Run the optimization workflow
results = workflow.start()  # Start the defined workflow process

# Print results from the workflow execution
print("\nEvaluator-Optimizer Results:")
for task_id, result in results["task_results"].items():  # Iterate through results of each task
    if result:  # Check if there is a result for the task
        print(f"Task {task_id}: {result.raw}")  # Print the raw result for each task

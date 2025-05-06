from praisonaiagents import Agent, Task, Agent4ALLAgents  # Import necessary classes for AI agents and tasks
import time  # Import time module for timestamps

def get_environment_state():
    """Simulates getting current environment state"""
    current_time = int(time.time())  # Get the current time as an integer
    states = ["normal", "critical", "optimal"]  # Define possible states
    state = states[current_time % 3]  # Determine state based on current time
    print(f"Environment state: {state}")  # Print the determined state
    return state  # Return the current state

def perform_action(state: str):
    """Simulates performing an action based on state"""
    # Map states to corresponding actions
    actions = {
        "normal": "maintain",   # Maintain the system in a normal state
        "critical": "fix",      # Fix issues in a critical state
        "optimal": "enhance"    # Enhance performance in an optimal state
    }
    action = actions.get(state, "observe")  # Get the action for the given state or default to 'observe'
    print(f"Performing action: {action} for state: {state}")  # Print the action being performed
    return action  # Return the action

def get_feedback():
    """Simulates environment feedback"""
    current_time = int(time.time())  # Get the current time as an integer
    # Determine feedback based on whether the current time is even or odd
    feedback = "positive" if current_time % 2 == 0 else "negative"
    print(f"Feedback received: {feedback}")  # Print the received feedback
    return feedback  # Return the feedback

# Create specialized agents with specific roles and responsibilities
llm_caller = Agent(
    name="Environment Monitor",  # Name of the agent
    role="State analyzer",  # Role description
    goal="Monitor environment and analyze state",  # Goal of the agent
    instructions="Check environment state and provide analysis",  # Instructions for the agent
    tools=[get_environment_state]  # Tools available to the agent
)

action_agent = Agent(
    name="Action Executor",  # Name of the agent
    role="Action performer",  # Role description
    goal="Execute appropriate actions based on state",  # Goal of the agent
    instructions="Determine and perform actions based on environment state",  # Instructions for the agent
    tools=[perform_action]  # Tools available to the agent
)

feedback_agent = Agent(
    name="Feedback Processor",  # Name of the agent
    role="Feedback analyzer",  # Role description
    goal="Process environment feedback and adapt strategy",  # Goal of the agent
    instructions="Analyze feedback and provide adaptation recommendations",  # Instructions for the agent
    tools=[get_feedback]  # Tools available to the agent
)

# Create tasks for an autonomous workflow, defining how agents interact
monitor_task = Task(
    name="monitor_environment",  # Task name
    description="Monitor and analyze environment state",  # Task description
    expected_output="Current environment state analysis",  # Expected output from the task
    agent=llm_caller,  # Agent responsible for this task
    is_start=True,  # Indicator for whether this is a starting task
    task_type="decision",  # Type of the task
    next_tasks=["execute_action"],  # Next task to execute
    condition={  # Conditions for proceeding with tasks
        "normal": ["execute_action"],  # If state is normal, execute action
        "critical": ["execute_action"],  # If state is critical, execute action
        "optimal": "exit"  # If state is optimal, exit the workflow
    }
)

action_task = Task(
    name="execute_action",  # Task name
    description="Execute appropriate action based on state",  # Task description
    expected_output="Action execution result",  # Expected output from the task
    agent=action_agent,  # Agent responsible for this task
    next_tasks=["process_feedback"]  # Next task to execute
)

feedback_task = Task(
    name="process_feedback",  # Task name
    description="Process feedback and adapt strategy",  # Task description
    expected_output="Strategy adaptation based on feedback",  # Expected output from the task
    agent=feedback_agent,  # Agent responsible for this task
    next_tasks=["monitor_environment"],  # Create a feedback loop by going back to monitoring
    context=[monitor_task, action_task]  # Provide access to previous task states and actions
)

# Create a workflow manager that orchestrates the tasks and agents
workflow = Agent4ALLAgents(
    agents=[llm_caller, action_agent, feedback_agent],  # List of agents involved
    tasks=[monitor_task, action_task, feedback_task],  # List of tasks in the workflow
    process="workflow",  # Type of process being managed
    verbose=True  # Set verbose to True for detailed output of the workflow execution
)

def main():
    """Main function to start the autonomous agent workflow"""
    print("\nStarting Autonomous Agent Workflow...")
    print("=" * 50)  # Separator

    # Run the autonomous workflow
    results = workflow.start()  # Start the workflow and capture the results

    # Print results of the workflow execution
    print("\nAutonomous Agent Results:")
    print("=" * 50)  # Separator
    for task_id, result in results["task_results"].items():  # Iterate through the task results
        if result:  # If there is a result for a task
            task_name = result.description  # Get the task description from result
            print(f"\nTask: {task_name}")  # Print the task name
            print(f"Result: {result.raw}")  # Print the raw result of the task
            print("-" * 50)  # Separator for clarity

if __name__ == "__main__":
    main()  # Run the main function if the script is executed directly

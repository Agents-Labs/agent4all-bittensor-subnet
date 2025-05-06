# Import necessary modules and classes
from praisonaiagents import Agent, Task, Agent4ALLAgents
import json
from e2b_code_interpreter import Sandbox

def code_interpreter(code: str):
    """
    A function to demonstrate running Python code dynamically using e2b_code_interpreter.
    
    Args:
        code (str): The Python code to be executed.

    Returns:
        str: A JSON string containing the results and logs of the executed code.
    """
    # Print the code that will be executed for visibility
    print(f"\n{'='*50}\n> Running following AI-generated code:\n{code}\n{'='*50}")
    
    # Run the provided code using the Sandbox environment
    exec_result = Sandbox().run_code(code)
    
    # Check if there was an error during execution
    if exec_result.error:
        print("[Code Interpreter error]", exec_result.error)
        return {"error": str(exec_result.error)}
    else:
        # Collect results from the execution
        results = []
        for result in exec_result.results:
            # If the result is iterable, extend the list; otherwise, append the result as a string
            if hasattr(result, '__iter__'):
                results.extend(list(result))
            else:
                results.append(str(result))
        
        # Collect standard output and error logs from execution
        logs = {"stdout": list(exec_result.logs.stdout), "stderr": list(exec_result.logs.stderr)}
        
        # Return the results and logs in JSON format
        return json.dumps({"results": results, "logs": logs})

# Create an agent responsible for generating Python code
code_agent = Agent(
    name="code_agent",            # Name of the agent
    llm="gpt-4o-mini",           # Language model used by the agent
    backstory="Expert in writing Python scripts",  # Background description for context
    self_reflect=False            # Whether the agent should reflect on its own outputs
)

# Create an agent responsible for executing Python code
execution_agent = Agent(
    name="execution_agent",       # Name of the agent
    llm="gpt-4o-mini",           # Language model used by the agent
    backstory="Expert in executing Python scripts",  # Background description for context
    self_reflect=False,           # Whether the agent should reflect on its own outputs
    tools=[code_interpreter]      # Tools available for the agent, including the code interpreter
)

# Define a task for the code agent to write a simple Python script
code_agent_task = Task(
    description="Write a simple Python script to print 'Hello, World!'",  # Task description
    expected_output="A Python script that prints 'Hello, World!'",        # Expected outcome of the task
    agent=code_agent              # Associate the task with the code agent
)

# Define a task for the execution agent to execute the generated Python script
execution_agent_task = Task(
    description="Execute the Python script",   # Task description
    expected_output="The output of the Python script",  # Expected outcome of the task
    agent=execution_agent         # Associate the task with the execution agent
)

# Create and initialize the set of agents and their tasks
agents = Agent4ALLAgents(agents=[code_agent, execution_agent], tasks=[code_agent_task, execution_agent_task])

# Start the agents and their task execution
agents.start()
# Import necessary modules and classes
from praisonaiagents import Agent, Task, Agent4ALLAgents
import json
from e2b_code_interpreter import Sandbox

def code_interpreter(code: str):
    """
    A function to demonstrate running Python code dynamically using e2b_code_interpreter.
    
    Args:
        code (str): The Python code to be executed.

    Returns:
        str: A JSON string containing the results and logs of the executed code.
    """
    # Print the code that will be executed for visibility
    print(f"\n{'='*50}\n> Running following AI-generated code:\n{code}\n{'='*50}")
    
    # Run the provided code using the Sandbox environment
    exec_result = Sandbox().run_code(code)
    
    # Check if there was an error during execution
    if exec_result.error:
        print("[Code Interpreter error]", exec_result.error)
        return {"error": str(exec_result.error)}
    else:
        # Collect results from the execution
        results = []
        for result in exec_result.results:
            # If the result is iterable, extend the list; otherwise, append the result as a string
            if hasattr(result, '__iter__'):
                results.extend(list(result))
            else:
                results.append(str(result))
        
        # Collect standard output and error logs from execution
        logs = {"stdout": list(exec_result.logs.stdout), "stderr": list(exec_result.logs.stderr)}
        
        # Return the results and logs in JSON format
        return json.dumps({"results": results, "logs": logs})

# Create an agent responsible for generating Python code
code_agent = Agent(
    name="code_agent",            # Name of the agent
    llm="gpt-4o-mini",           # Language model used by the agent
    backstory="Expert in writing Python scripts",  # Background description for context
    self_reflect=False            # Whether the agent should reflect on its own outputs
)

# Create an agent responsible for executing Python code
execution_agent = Agent(
    name="execution_agent",       # Name of the agent
    llm="gpt-4o-mini",           # Language model used by the agent
    backstory="Expert in executing Python scripts",  # Background description for context
    self_reflect=False,           # Whether the agent should reflect on its own outputs
    tools=[code_interpreter]      # Tools available for the agent, including the code interpreter
)

# Define a task for the code agent to write a simple Python script
code_agent_task = Task(
    description="Write a simple Python script to print 'Hello, World!'",  # Task description
    expected_output="A Python script that prints 'Hello, World!'",        # Expected outcome of the task
    agent=code_agent              # Associate the task with the code agent
)

# Define a task for the execution agent to execute the generated Python script
execution_agent_task = Task(
    description="Execute the Python script",   # Task description
    expected_output="The output of the Python script",  # Expected outcome of the task
    agent=execution_agent         # Associate the task with the execution agent
)

# Create and initialize the set of agents and their tasks
agents = Agent4ALLAgents(agents=[code_agent, execution_agent], tasks=[code_agent_task, execution_agent_task])

# Start the agents and their task execution
agents.start()

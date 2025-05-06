from praisonaiagents import Agent, Task, Agent4ALLAgents, error_logs
from duckduckgo_search import DDGS

def my_callback(output):
    # Callback function to handle output from tasks
    print(f"Callback Task output: {output}")

def internet_search_tool(query) -> list:
    """
    Perform a search using DuckDuckGo.

    Args:
        query (str): The search query.

    Returns:
        list: A list of search result titles and URLs.
    """
    try:
        results = []  # Initialize an empty list to store search results
        ddgs = DDGS()  # Create an instance of the DuckDuckGo search API
        # Perform the search and retrieve up to 10 results
        for result in ddgs.text(keywords=query, max_results=10):
            results.append({
                "title": result.get("title", ""),  # Fetch and store the title of each result
                "url": result.get("href", ""),      # Fetch and store the URL of each result
                "snippet": result.get("body", "")    # Fetch and store a snippet of each result
            })
        return results  # Return the list of formatted search results

    except Exception as e:
        # Handle any exceptions that might occur during the search
        print(f"Error during DuckDuckGo search: {e}")
        return []  # Return an empty list in case of error

# Create agents
# Agent for researching AI advancements
researcher = Agent(
    name="Researcher",  # Name of the agent
    role="Senior Research Analyst",  # Role of the agent
    goal="Uncover cutting-edge developments in AI and data science",  # The agent's goal
    backstory="""You are an expert at a technology research group, 
    skilled in identifying trends and analyzing complex data.""",  # Background information
    verbose=True,  # Set verbose output for debugging
    allow_delegation=False,  # Prevent this agent from delegating tasks
    tools=[internet_search_tool],  # Assign the internet search tool
    llm="gpt-4o",  # Specify the language model to use
    markdown=True,  # Enable Markdown formatting
    reflect_llm="gpt-4o",  # Language model for self-reflection
    min_reflect=2,  # Minimum reflection depth
    max_reflect=4   # Maximum reflection depth
)

# Agent for writing content
writer = Agent(
    name="Writer",  # Name of the agent
    role="Tech Content Strategist",  # Role of the agent
    goal="Craft compelling content on tech advancements",  # The agent's goal
    backstory="""You are a content strategist known for 
    making complex tech topics interesting and easy to understand.""",  # Background information
    verbose=True,  # Set verbose output for debugging
    allow_delegation=True,  # Allow this agent to delegate tasks
    llm="gpt-4o",  # Specify the language model to use
    tools=[],  # No specific tools assigned for this agent
    markdown=True  # Enable Markdown formatting
)

# Create tasks
# Task to research AI advancements
task1 = Task(
    name="research_task",  # Name of the task
    description="""Analyze 2024's AI advancements. 
    Find major trends, new technologies, and their effects.""",  # Description of the task
    expected_output="""A detailed report on 2024 AI advancements""",  # Expected output of the task
    agent=researcher,  # Assign the researcher agent to this task
    tools=[internet_search_tool]  # Specify the tools to use for this task
)

# Task to write a blog post based on research findings
task2 = Task(
    name="writing_task",  # Name of the task
    description="""Create a blog post about major AI advancements using the insights you have.
    Make it interesting, clear, and suited for tech enthusiasts. 
    It should be at least 4 paragraphs long. 
    Also, call the get_weather tool to get the weather in Paris.""",  # Task description
    expected_output="A blog post of at least 4 paragraphs, and weather in Paris",  # Expected output
    agent=writer,  # Assign the writer agent to this task
    context=[task1],  # Provide the output of the research task as context
    callback=my_callback,  # Assign a callback function for task output
    tools=[]  # No specific tools are assigned for this task
)

# Task to create a JSON object
task3 = Task(
    name="json_task",  # Name of the task
    description="""Create a json object with a title of "My Task" and content of "My content".""",  # Task description
    expected_output="""JSON output with title and content""",  # Expected output
    agent=researcher,  # Assign the researcher agent to this task
)

# Task to save the output to a file
task4 = Task(
    name="save_output_task",  # Name of the task
    description="""Save the AI blog post to a file""",  # Task description
    expected_output="""File saved successfully""",  # Expected output
    agent=writer,  # Assign the writer agent to this task
    context=[task2],  # Provide the output of the writing task as context
    output_file='outputs/ai_blog_post.txt',  # Path to save the output file
    create_directory=True  # Option to create the directory if it does not exist
)

# Create and run agents manager
agents = Agent4ALLAgents(
    agents=[researcher, writer],  # List of agents involved in the workflow
    tasks=[task1, task2, task3, task4],  # List of tasks to execute
    verbose=False,  # Set verbosity for overall agent manager
    process="sequential",  # Define processing mode, can be "sequential" or "hierarchical"
    manager_llm="gpt-4o"  # Language model for the agents manager
)

result = agents.start()  # Start the agent workflow and store the result

# Print results and error summary
print("\n=== Task Results ===")  # Header for task results output
for task_id, task_status in result['task_status'].items():
    print(f"Task {task_id}: {task_status}")  # Print each task's ID and its execution status
    if task_result := result['task_results'].get(task_id):
        print(f"Output: {task_result.raw[:200]}...")  # Display the first 200 chars of each task's output

# Print task details
print("\n=== Task Details ===")  # Header for task details output
for i in range(4):
    print(agents.get_task_details(i))  # Print details of each task

# Print agent details
print("\n=== Agent Details ===")  # Header for agent details output
print(agents.get_agent_details('Researcher'))  # Print details of the Researcher agent
print(agents.get_agent_details('Writer'))  # Print details of the Writer agent

# Print any errors encountered during the workflow
if error_logs:  # Check if there are any error logs
    print("\n=== Error Summary ===")  # Header for error summary output
    for err in error_logs:
        print(f"- {err}")  # Print each error message
        if "parsing self-reflection json" in err:  # Specific error handling for JSON parsing
            print("  Reason: The self-reflection JSON response was not valid JSON.")
        elif "Error: Task with ID" in err:  # Specific error handling for invalid task ID
            print("  Reason: Task ID referenced does not exist.")
        elif "saving task output to file" in err:  # Specific error handling for file saving issues
            print("  Reason: Possible file permissions or invalid path.")
        else:
            print("  Reason not identified")  # General error case

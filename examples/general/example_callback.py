from praisonaiagents import (
    Agent, 
    Task, 
    Agent4ALLAgents, 
    error_logs, 
    register_display_callback,
    sync_display_callbacks,
    async_display_callbacks
)
from duckduckgo_search import DDGS
from rich.console import Console
import json
from datetime import datetime
import logging

# Setup logging configuration for tracking interactions and errors
logging.basicConfig(
    filename='ai_interactions.log',  # Log file name
    level=logging.INFO,               # Set log level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
)

# Callback functions for different display types
def interaction_callback(message=None, response=None, markdown=None, generation_time=None):
    """Callback for display_interaction, logs details of the interaction."""
    logging.info(f"""
    === INTERACTION ===
    Time: {datetime.now()}              # Current timestamp
    Generation Time: {generation_time}s   # Time taken for generation
    Message: {message}                    # User message
    Response: {response}                  # AI's response
    Markdown: {markdown}                  # Any markdown content
    """)

def error_callback(message=None):
    """Callback for display_error, logs errors that occur."""
    logging.error(f"""
    === ERROR ===
    Time: {datetime.now()}                # Timestamp of the error
    Message: {message}                     # Error message
    """)

def tool_call_callback(message=None):
    """Callback for display_tool_call, logs tool usage information."""
    logging.info(f"""
    === TOOL CALL ===
    Time: {datetime.now()}               # Current timestamp
    Message: {message}                   # Message detailing tool call
    """)

def instruction_callback(message=None):
    """Callback for display_instruction, logs instructions provided."""
    logging.info(f"""
    === INSTRUCTION ===
    Time: {datetime.now()}               # Current timestamp
    Message: {message}                   # Instruction message
    """)

def self_reflection_callback(message=None):
    """Callback for display_self_reflection, logs self-reflection messages."""
    logging.info(f"""
    === SELF REFLECTION ===
    Time: {datetime.now()}               # Current timestamp
    Message: {message}                   # Self-reflection message
    """)

def generating_callback(content=None, elapsed_time=None):
    """Callback for display_generating, logs content being generated."""
    logging.info(f"""
    === GENERATING ===
    Time: {datetime.now()}               # Current timestamp
    Content: {content}                   # Content currently being generated
    Elapsed Time: {elapsed_time}         # Time taken for content generation
    """)

# Register all callbacks to the respective loggers
register_display_callback('interaction', interaction_callback)
register_display_callback('error', error_callback)
register_display_callback('tool_call', tool_call_callback)
register_display_callback('instruction', instruction_callback)
register_display_callback('self_reflection', self_reflection_callback)
# register_display_callback('generating', generating_callback)  # Commented out for now

def task_callback(output):
    """Callback for task completion, logs details of the task output."""
    logging.info(f"""
    === TASK COMPLETED ===
    Time: {datetime.now()}                  # Current timestamp
    Description: {output.description}        # Description of the task
    Agent: {output.agent}                    # The agent that completed the task
    Output: {output.raw[:200]}...            # Output from the task (truncated)
    """)

def internet_search_tool(query) -> list:
    """
    Perform a search using DuckDuckGo.

    Args:
        query (str): The search query.

    Returns:
        list: A list of search result titles and URLs.
    """
    try:
        results = []                  # Initialize an empty list for results
        ddgs = DDGS()                # Create a DuckDuckGo search instance
        # Perform search and collect results
        for result in ddgs.text(keywords=query, max_results=10):
            results.append({
                "title": result.get("title", ""),  # Title of the search result
                "url": result.get("href", ""),    # URL of the search result
                "snippet": result.get("body", "")  # Snippet of the search result
            })
        return results                # Return the list of results

    except Exception as e:
        print(f"Error during DuckDuckGo search: {e}")  # Print error message
        return []                    # Return empty list on error

def main():
    # Create agents with specific roles and attributes
    researcher = Agent(
        name="Researcher",
        role="Senior Research Analyst",
        goal="Uncover cutting-edge developments in AI and data science",
        backstory="""You are an expert at a technology research group, 
        skilled in identifying trends and analyzing complex data.""",
        verbose=True,                  # Enable verbose output
        allow_delegation=False,        # Prevent delegation of tasks
        tools=[internet_search_tool],  # Assign the internet search tool to the agent
        llm="gpt-4o",                  # Language model to be used
        markdown=True,                 # Enable markdown formatting
        reflect_llm="gpt-4o",          # Language model for self-reflection
        min_reflect=2,                 # Minimum reflect count
        max_reflect=4                  # Maximum reflect count
    )
    
    writer = Agent(
        name="Writer",
        role="Tech Content Strategist",
        goal="Craft compelling content on tech advancements",
        backstory="""You are a content strategist known for 
        making complex tech topics interesting and easy to understand.""",
        verbose=True,                  # Enable verbose output
        allow_delegation=True,         # Allow delegation of tasks
        llm="gpt-4o",                  # Language model to be used
        tools=[],                      # No external tools for the writer agent
        markdown=True                   # Enable markdown formatting
    )

    # Define tasks to be assigned to agents with callbacks for completion
    task1 = Task(
        name="research_task",
        description="""Analyze 2024's AI advancements. 
        Find major trends, new technologies, and their effects.""",
        expected_output="""A detailed report on 2024 AI advancements""",
        agent=researcher,                  # Assign researcher agent
        tools=[internet_search_tool],      # Assign tools needed for task
        callback=task_callback             # Callback for task completion
    )

    task2 = Task(
        name="writing_task",
        description="""Create a blog post about major AI advancements using the insights you have.
        Make it interesting, clear, and suited for tech enthusiasts. 
        It should be at least 4 paragraphs long.""",
        expected_output="A blog post of at least 4 paragraphs",
        agent=writer,                      # Assign writer agent
        context=[task1],                  # Reference previous research task
        callback=task_callback,            # Callback for task completion
        tools=[]                           # No external tools needed for this task
    )

    task3 = Task(
        name="json_task",
        description="""Create a json object with a title of "My Task" and content of "My content".""",
        expected_output="""JSON output with title and content""",
        agent=researcher,                  # Assign researcher agent
        callback=task_callback             # Callback for task completion
    )

    task4 = Task(
        name="save_output_task",
        description="""Save the AI blog post to a file""",
        expected_output="""File saved successfully""",
        agent=writer,                      # Assign writer agent
        context=[task2],                  # Reference previous writing task
        output_file='test.txt',           # Specify output file name
        create_directory=True,             # Create directory if needed
        callback=task_callback             # Callback for task completion
    )

    # Create and run agents manager to handle the agents and tasks
    agents = Agent4ALLAgents(
        agents=[researcher, writer],       # List of agents to be managed
        tasks=[task1, task2, task3, task4],  # List of tasks to be executed
        verbose=True,                      # Enable verbose output
        process="sequential",              # Process tasks sequentially
        manager_llm="gpt-4o"               # Language model for the manager
    )

    agents.start()                        # Start the agents manager

if __name__ == "__main__":
    main()                                 # Execute main function

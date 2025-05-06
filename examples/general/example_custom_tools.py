from praisonaiagents import Agent, Task, Agent4ALLAgents
from typing import List, Dict, Union
from duckduckgo_search import DDGS
from langchain_community.tools import YouTubeSearchTool
from langchain_community.utilities import WikipediaAPIWrapper

# 1. Tool Definitions
def internet_search_tool(query: str) -> List[Dict]:
    """
    Perform a search using DuckDuckGo.

    Args:
        query (str): The search query.

    Returns:
        list: A list of search result titles, URLs, and snippets.
    """
    try:
        results = []  # Initialize the results list
        ddgs = DDGS()  # Create an instance of DuckDuckGo search
        for result in ddgs.text(keywords=query, max_results=10):  # Perform the search with a maximum of 10 results
            results.append({
                "title": result.get("title", ""),  # Get the title of the search result
                "url": result.get("href", ""),      # Get the URL of the search result
                "snippet": result.get("body", "")    # Get the snippet (summary) of the search result
            })
        return results  # Return the list of results

    except Exception as e:
        print(f"Error during DuckDuckGo search: {e}")  # Log any errors that occur
        return []  # Return an empty list in case of error
    
def youtube_search_tool(query: str, inspect: bool = False, max_results: int = 2):
    """
    Provide a custom wrapper around the YouTubeSearchTool.
    
    Args:
        query (str): The search query for YouTube.
        inspect (bool): If True, returns tool inspection info instead of search results.
        max_results (int): Maximum number of results to return (default: 2).
        
    Returns:
        Union[List[str], dict]: List of YouTube video URLs or tool inspection info.
    """
    yt = YouTubeSearchTool()  # Create an instance of the YouTube search tool
    
    if inspect:  # If inspection info is requested
        # Compile inspection info about the tool
        inspection_info = {
            "type": type(yt),
            "attributes": [attr for attr in dir(yt) if not attr.startswith('_')],  # Get public attributes
            "methods": {
                "run": getattr(yt, 'run', None),  # Get the 'run' method
                "arun": getattr(yt, 'arun', None)  # Get the 'arun' method (if available)
            },
            "properties": {
                "name": getattr(yt, 'name', 'youtube_search'),  # Get the name of the tool
                "description": getattr(yt, 'description', 'Search YouTube videos'),  # Get the description
                "return_direct": getattr(yt, 'return_direct', False)  # Get return_direct property
            }
        }
        return inspection_info  # Return the inspection info
    
    # Format query including the maximum number of results
    formatted_query = f"{query}, {max_results}"
    return yt.run(formatted_query)  # Perform the YouTube search and return results

def wikipedia_search_tool(query: str, inspect: bool = False, max_chars: int = 4000, top_k: int = 3):
    """
    Provide a custom wrapper around langchain_community's WikipediaAPIWrapper.

    Args:
        query (str): A search query for Wikipedia.
        inspect (bool): If True, returns tool inspection info instead of search results.
        max_chars (int): Maximum characters to return (default: 4000).
        top_k (int): Number of top results to consider (default: 3).
        
    Returns:
        Union[str, dict]: Summary from Wikipedia or tool inspection info if inspect=True.
    """
    # Create an instance of the Wikipedia API wrapper
    w = WikipediaAPIWrapper(
        top_k_results=top_k,               # Set the number of top results to retrieve
        doc_content_chars_max=max_chars,   # Set the maximum character limit for returned content
        lang='en'                           # Specify the language for the search
    )
    
    if inspect:  # If inspection info is requested
        # Compile inspection info about the Wikipedia API wrapper
        inspection_info = {
            "type": type(w),
            "attributes": [attr for attr in dir(w) if not attr.startswith('_')],  # Get public attributes
            "methods": {
                "run": getattr(w, 'run', None),  # Get the 'run' method
                "arun": getattr(w, 'arun', None)  # Get the 'arun' method (if available)
            },
            "properties": {
                "name": "wikipedia",  # Set the name
                "description": "Search and get summaries from Wikipedia",  # Set the description
                "top_k": w.top_k_results,  # Get the number of top results setting
                "lang": w.lang,  # Get the language setting
                "max_chars": w.doc_content_chars_max  # Get the maximum characters setting
            }
        }
        return inspection_info  # Return the inspection info
    
    try:
        result = w.run(query)  # Perform the Wikipedia search
        return result  # Return the search result
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"  # Return error message if any exception occurs

# 2. Agent Definition
data_agent = Agent(
    name="DataCollector",  # The name of the agent
    role="Search Specialist",  # The role of the agent
    goal="Perform internet searches to collect relevant information.",  # The agent's goal
    backstory="Expert in finding and organizing internet data from multiple sources.",  # Background information
    tools=[internet_search_tool, youtube_search_tool, wikipedia_search_tool],  # Assign the tools available to the agent
    self_reflect=False  # Whether the agent can self-reflect (used for advanced scenarios)
)

# 3. Tasks Definition
# Task to collect data via internet searches
collect_task = Task(
    description="Perform an internet search using the query: 'AI job trends in 2024'. Return results as a list of title, URL, and snippet.",
    expected_output="List of search results with titles, URLs, and snippets.",  # Define the expected output of this task
    agent=data_agent,  # Assign the agent responsible for this task
    name="collect_data",  # Name of the task
    is_start=True,  # Mark this as the starting task
    next_tasks=["validate_data"]  # Define the next task after this one
)

# Task to validate the collected data
validate_task = Task(
    description="""Validate the collected data. Check if:
    1. At least 5 results are returned.
    2. Each result contains a title and a URL.
    Return validation_result as 'valid' or 'invalid' only no other text.""",
    expected_output="Validation result indicating if data is valid or invalid.",  # Define the expected validation result
    agent=data_agent,  # Assign the agent responsible for this validation task
    name="validate_data",  # Name of the task
    task_type="decision",  # Define this task as a decision-making task
    condition={
        "valid": [],  # End the workflow if data is valid
        "invalid": ["collect_data"]  # Retry data collection if data is invalid
    },
)

# 4. Workflow Definition
# Setting up the agents and tasks in a workflow
agents = Agent4ALLAgents(
    agents=[data_agent],  # List of agents defined
    tasks=[collect_task, validate_task],  # List of tasks to be performed
    verbose=1,  # Verbose output level for debugging and logging
    process="workflow"  # Define the type of processing
)

# Start the workflow with the defined agents and tasks
agents.start()

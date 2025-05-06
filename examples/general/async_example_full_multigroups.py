import asyncio
import time
from typing import List, Dict
from praisonaiagents import Agent, Task, Agent4ALLAgents, TaskOutput
from duckduckgo_search import DDGS
from pydantic import BaseModel

# 1. Define output model for structured results
class SearchResult(BaseModel):
    query: str               # The search query that was executed
    results: List[Dict[str, str]]  # List of search results, each containing title, URL, and snippet
    total_results: int       # Total number of results returned

# 2. Define async search tool
async def async_search_tool(query: str) -> Dict:
    """
    Asynchronous search using DuckDuckGo.
    Args:
        query (str): The search query.
    Returns:
        dict: Search results in SearchResult model format
    """
    await asyncio.sleep(1)  # Simulate network delay to mimic real-world conditions
    try:
        results = []  # Initialize list to store search results
        ddgs = DDGS()  # Create an instance of DuckDuckGo search client
        for result in ddgs.text(keywords=query, max_results=5):  # Perform the search query
            results.append({
                "title": result.get("title", ""),  # Get the result title
                "url": result.get("href", ""),     # Get the result URL
                "snippet": result.get("body", "")   # Get the snippet of the result
            })

        # Format response to match SearchResult model
        return {
            "query": query,                      # Return the original query
            "results": results,                  # Return the list of results
            "total_results": len(results)        # Return the count of results
        }
    except Exception as e:
        print(f"Error during async search: {e}")  # Error handling during the search operation
        return {
            "query": query,
            "results": [],
            "total_results": 0                    # Return zero results in case of error
        }

# 3. Define async callback
async def async_callback(output: TaskOutput):
    await asyncio.sleep(1)  # Simulate processing delay
    # Output handling based on the expected format
    if output.output_format == "JSON":
        print(f"Processed JSON result: {output.json_dict}")  # Print JSON output
    elif output.output_format == "Pydantic":
        print(f"Processed Pydantic result: {output.pydantic}")  # Print Pydantic output

# 4. Create specialized agents
async_agent = Agent(
    name="AsyncSearchAgent",
    role="Asynchronous Search Specialist",
    goal="Perform fast and efficient asynchronous searches with structured results",
    backstory="Expert in parallel search operations and data retrieval",
    tools=[async_search_tool],           # Associate the search tool with the agent
    self_reflect=False,
    verbose=True,                        # Enable verbose output for debugging
    markdown=True
)

summary_agent = Agent(
    name="SummaryAgent",
    role="Research Synthesizer",
    goal="Create comprehensive summaries and identify patterns across multiple search results",
    backstory="""Expert in analyzing and synthesizing information from multiple sources.
Skilled at identifying patterns, trends, and connections between different topics.
Specializes in creating clear, structured summaries that highlight key insights.""",
    self_reflect=True,  # Enable self-reflection for better summary quality
    verbose=True,       # Verbose output to track summarization process
    markdown=True
)

# 5. Create async tasks
async_task = Task(
    name="async_search",
    description="""Search for 'Async programming' and return results in the following JSON format:
{
    "query": "the search query",
    "results": [
        {
            "title": "result title",
            "url": "result url",
            "snippet": "result snippet"
        }
    ],
    "total_results": number of results
}""",
    expected_output="SearchResult model with query details and results",  # Expected format of output
    agent=async_agent,            # The async search agent assigned to this task
    async_execution=True,         # Specify that the task will run asynchronously
    callback=async_callback,      # Define the callback function to handle output
    output_json=SearchResult      # Define the output JSON model
)

# 6. Example usage functions
async def run_single_task():
    """Run single async task"""
    print("\nRunning Single Async Task...")
    agents = Agent4ALLAgents(
  

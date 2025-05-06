import asyncio
import time
from typing import List, Dict
from praisonaiagents import Agent, Task, Agent4ALLAgents, TaskOutput
from duckduckgo_search import DDGS
from pydantic import BaseModel

# 1. Define output model for structured results
class SearchResult(BaseModel):
    """Model to structure the search results returned by the async search tool."""
    query: str  # The search query used to fetch results
    results: List[Dict[str, str]]  # List of search results, each represented as a dictionary
    total_results: int  # Total number of results found

# 2. Define async tool
async def async_search_tool(query: str) -> Dict:
    """Perform asynchronous search and return structured results."""
    await asyncio.sleep(1)  # Simulate a network delay for search (e.g., waiting for API response)
    try:
        results = []  # Initialize a list to hold the search results
        ddgs = DDGS()  # Initialize the DuckDuckGo search client
        # Perform a text search using the DuckDuckGo client
        for result in ddgs.text(keywords=query, max_results=5):
            results.append({
                "title": result.get("title", ""),  # Get the title of the search result
                "url": result.get("href", ""),     # Get the URL of the search result
                "snippet": result.get("body", "")   # Get a brief snippet/description of the result
            })
        
        return {
            "query": query,                      # Return the original search query
            "results": results,                  # Return the list of search results
            "total_results": len(results)        # Provide the total number of results found
        }
    except Exception as e:
        # Handle any exceptions that occur during the search process
        print(f"Error during async search: {e}")
        return {
            "query": query,                      # Return the query even if an error occurred
            "results": [],                       # Empty results on error
            "total_results": 0                   # Indicate no results were found due to error
        }

# 3. Define async callback
async def async_callback(output: TaskOutput):
    """Callback function to process the output from a task."""
    await asyncio.sleep(1)  # Simulate additional processing time after receiving the output
    if output.output_format == "JSON":
        # Process output if it's in JSON format
        print(f"Processed JSON result: {output.json_dict}")  # Print the processed JSON result
    elif output.output_format == "Pydantic":
        # Process output if it's in Pydantic format
        print(f"Processed Pydantic result: {output.pydantic}")  # Print the processed Pydantic result

# 4. Create specialized agents
async_agent = Agent(
    name="AsyncSearchAgent",  # Name of the agent responsible for performing asynchronous searches
    role="Search Specialist",  # Role description of the agent
    goal="Perform fast parallel searches with structured results",  # Agent's goal
    backstory="Expert in efficient data retrieval and parallel search operations",  # Background description
    tools=[async_search_tool],  # List of tools this agent can utilize
    self_reflect=False,  # Indicates that the agent does not reflect on its own process
    verbose=True,  # Enables verbose output for debugging
    markdown=True   # Enables markdown rendering for output where applicable
)

summary_agent = Agent(
    name="SummaryAgent",  # Name of the summarization agent
    role="Research Synthesizer",  # Role description of the summary agent
    goal="Create concise summaries from multiple search results",  # Summary agent's goal
    backstory="Expert in analyzing and synthesizing information from multiple sources",  # Background of the summary agent
    self_reflect=True,  # Indicates that the agent can reflect on its own process
    verbose=True,  # Enables verbose output for debugging
    markdown=True   # Enables markdown for output where applicable
)

# 5. Create async tasks for searching
async_task = Task(
    name="async_search",  # Name of the search task
    description="Search for 'Async programming' and return results in JSON format with query, results array, and total_results count.", 
    expected_output="SearchResult model with structured data",  # Expected output format
    agent=async_agent,  # Assign the async search agent
    async_execution=True,  # Indicate that this task is to be executed asynchronously
    callback=async_callback,  # Assign the callback function to process output
    output_json=SearchResult  # Define the expected output format using the SearchResult model
)

async def run_parallel_tasks():
    """Run multiple async tasks in parallel."""
    print("\nRunning Parallel Async Tasks...")
    
    # Define different search topics for parallel processing
    search_topics = [
        "Latest AI Developments 2024",
        "Machine Learning Best Practices",
        "Neural Networks Architecture"
    ]
    
    # Create tasks for different search topics
    parallel_tasks = [
        Task(
            name=f"search_task_{i}",  # Unique name for each task based on its index
            description=f"Search for '{topic}' and return structured results with query details and findings.",  # Description of the task
            expected_output="SearchResult model with search data",  # Expected data format for output
            agent=async_agent,  # Assign the async agent to perform the search
            async_execution=True,  # Indicate that the task should run asynchronously
            callback=async_callback,  # Assign the callback to process the output results
            output_json=SearchResult  # Define the expected output format
        ) for i, topic in enumerate(search_topics)  # Create a task for each topic
    ]
    
    # Create a summarization task that will analyze results from previous searches
    summary_task = Task(
        name="summary_task",  # Name of the summarization task
        description="Analyze all search results and create a concise summary highlighting key findings, patterns, and implications.",  # Summary task description
        expected_output="Structured summary with key findings and insights",  # Expected output format
        agent=summary_agent,  # Assign the summary agent to perform the analysis
        async_execution=False,  # This task will execute synchronously after the search tasks complete
        callback=async_callback,  # Assign the callback to process the summarization output
        context=parallel_tasks  # Provide context for the summary task as previously created search tasks
    )
    
    # Create a single Agent4ALLAgents instance with both agents and tasks
    agents = Agent4ALLAgents(
        agents=[async_agent, summary_agent],  # List of agents to manage
        tasks=parallel_tasks + [summary_task],  # Combine the previously created tasks into one list
        verbose=1,  # Set verbosity level
        process="sequential"  # Specify that tasks should be executed sequentially
    )
    
    # Run all tasks asynchronously
    results = await agents.astart()  # Start the task execution and wait for completion
    print(f"Tasks Results: {results}")  # Print the resulting tasks' output

    # Return results in a serializable format
    return {
        "search_results": {
            "task_status": {k: v for k, v in results["task_status"].items() if k != summary_task.id},  # Gather status of all search tasks excluding summary task
            "task_results": [str(results["task_results"][i]) if results["task_results"][i] else None 
                             for i in range(len(parallel_tasks))]  # Collect results of each search task
        },
        "summary": str(results["task_results"][summary_task.id]) if results["task_results"].get(summary_task.id) else None,  # Summarization result
        "topics": search_topics  # Include the search topics in the return value
    }

# 6. Main execution
async def main():
    """Main execution function that starts the async tasks."""
    print("Starting Async AI Agents Examples...")  # Indicate start of program execution
    
    try:
        await run_parallel_tasks()  # Call the function to run all the defined tasks asynchronously
    except Exception as e:
        # Handle any exceptions that occur during the main execution
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    # Entry point for the program
    asyncio.run(main())  # Execute the main function within the asyncio event loop

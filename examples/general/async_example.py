import asyncio
import time
from typing import List, Dict
from praisonaiagents import Agent, Task, Agent4ALLAgents, TaskOutput
from praisonaiagents.main import (
    display_error,
    display_interaction,
    display_tool_call,
    display_instruction,
    error_logs,
    Console
)
from duckduckgo_search import DDGS
from pydantic import BaseModel

console = Console()

# 1. Define output model for structured results using Pydantic.
class SearchResult(BaseModel):
    query: str
    results: List[Dict[str, str]]
    total_results: int

# 2. Define both synchronous and asynchronous search tools.
def sync_search_tool(query: str) -> List[Dict]:
    """
    Synchronous search using DuckDuckGo.
    Args:
        query (str): The search query.
    Returns:
        List[Dict]: A list of search results as dictionaries.
    """
    display_tool_call(f"Running sync search for: {query}", console)
    time.sleep(1)  # Simulate network delay
    try:
        results = []
        ddgs = DDGS()  # Initialize DuckDuckGo search client
        for result in ddgs.text(keywords=query, max_results=5):
            # Append results to list with title, URL, and snippet
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })
        return results
    except Exception as e:
        error_msg = f"Error during sync search: {e}"
        display_error(error_msg, console)
        error_logs.append(error_msg)  # Log error
        return []

async def async_search_tool(query: str) -> List[Dict]:
    """
    Asynchronous search using DuckDuckGo.
    Args:
        query (str): The search query.
    Returns:
        List[Dict]: A list of search results as dictionaries.
    """
    display_tool_call(f"Running async search for: {query}", console)
    await asyncio.sleep(1)  # Simulate network delay
    try:
        results = []
        ddgs = DDGS()  # Initialize DuckDuckGo search client
        for result in ddgs.text(keywords=query, max_results=5):
            # Append results to list with title, URL, and snippet
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })
        return results
    except Exception as e:
        error_msg = f"Error during async search: {e}"
        display_error(error_msg, console)
        error_logs.append(error_msg)  # Log error
        return []

# 3. Define callback functions for handling output from tasks.
def sync_callback(output: TaskOutput):
    """
    Process output for synchronous task.
    Args:
        output (TaskOutput): The output from the task.
    """
    display_interaction("Sync Callback", f"Processing output: {output.raw[:100]}...", markdown=True, console=console)
    time.sleep(1)  # Simulate processing
    if output.output_format == "JSON":
        display_tool_call(f"Processed JSON result: {output.json_dict}", console)
    elif output.output_format == "Pydantic":
        display_tool_call(f"Processed Pydantic result: {output.pydantic}", console)

async def async_callback(output: TaskOutput):
    """
    Process output for asynchronous task.
    Args:
        output (TaskOutput): The output from the task.
    """
    dis

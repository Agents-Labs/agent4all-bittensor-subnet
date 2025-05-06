# Import necessary classes from the praisonaiagents package
from praisonaiagents import Agent, Task, Agent4ALLAgents
from praisonaiagents.tools import wiki_search, wiki_summary, wiki_page, wiki_random, wiki_language

# Create an instance of the Agent class with specific instructions for usage
# This agent is designated as a "Wikipedia Agent" and is equipped with various Wikipedia tools
agent = Agent(
    instructions="You are a Wikipedia Agent",  # Instructions for the agent's behavior
    tools=[wiki_search, wiki_summary, wiki_page, wiki_random, wiki_language],  # Tools the agent can utilize
    self_reflect=True,  # Enable self-reflection for the agent's responses
    min_reflect=3,  # Minimum instances of self-reflection during its tasks
    max_reflect=5,  # Maximum instances of self-reflection during its tasks
)

# Start the agent with a specific task consisting of multiple actions
# The agent will first search the history of AI, then read the respective Wikipedia page,
# and finally, summarize the page's content.
agent.start(
    "What is the history of AI?"  # Initial question to the agent
    " First search the history of AI"  # Task to perform a search
    " Read the page of the history of AI"  # Task to read the details of the page
    " Get the summary of the page"  # Task to summarize the findings
)

from praisonaiagents import Agent, Agent4ALLAgents
from langchain_community.tools import TavilySearchResults

def search_tool(query: str):
    tool = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=True
    )
    return tool.run(query)

data_agent = Agent(instructions="I am looking for the top google searches on AI tools of 2025", tools=[search_tool])
editor_agent = Agent(instructions="Analyze the data and rank the tools based on their popularity")

agents = Agent4ALLAgents(agents=[data_agent, editor_agent])
agents.start()
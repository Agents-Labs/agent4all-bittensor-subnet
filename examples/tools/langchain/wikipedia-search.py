from praisonaiagents import Agent, Agent4ALLAgents
from langchain_community.utilities import WikipediaAPIWrapper

data_agent = Agent(instructions="Gather all of Messi's record in LaLiga", tools=[WikipediaAPIWrapper])
summarise_agent = Agent(instructions="Summarize the data into a well structured format")
agents = Agent4ALLAgents(agents=[data_agent, summarise_agent])
agents.start()
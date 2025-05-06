import os 
from langchain_google_community import GoogleSearchAPIWrapper
from praisonaiagents import Agent, Agent4ALLAgents

data_agent = Agent(instructions="Search about best places to visit in India during Summer", tools=[GoogleSearchAPIWrapper])
editor_agent = Agent(instructions="Write a blog article")
agents = Agent4ALLAgents(agents=[data_agent, editor_agent], process='hierarchical')
agents.start()
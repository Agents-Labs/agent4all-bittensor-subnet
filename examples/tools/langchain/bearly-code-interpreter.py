from praisonaiagents import Agent, Agent4ALLAgents
from langchain_community.tools import BearlyInterpreterTool

coder_agent = Agent(instructions="""for i in range(0,10):
                                        print(f'The number is {i}')""", tools=[BearlyInterpreterTool])

agents = Agent4ALLAgents(agents=[coder_agent])
agents.start()
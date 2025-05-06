from praisonaiagents import Agent, Agent4ALLAgents
import getpass
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool

POOL_MANAGEMENT_ENDPOINT = getpass.getpass()

coder_agent = Agent(instructions="""word = "strawberry"
                                    count = word.count("r")
                                    print(f"There are {count}'R's in the word 'Strawberry'")""", tools=[SessionsPythonREPLTool])

agents = Agent4ALLAgents(agents=[coder_agent])
agents.start()
# Import necessary modules and classes from the praisonaiagents library
from praisonaiagents import Agent, Tools
from praisonaiagents.tools import read_csv, read_excel, write_csv, write_excel, filter_data, get_summary, group_by, pivot_table
import os

# Initialize the Agent with specific instructions and tools it can use
agent = Agent(
    instructions="You are a Data Analyst Agent", 
    tools=[
        read_csv, 
        read_excel, 
        write_csv, 
        write_excel, 
        filter_data, 
        get_summary, 
        group_by, 
        pivot_table
    ]
)

# Start the agent with a task, providing it with the necessary CSV file path and describing the actions to take
agent.start(f"""
    Read the data from the csv file {os.path.join(os.path.dirname(__file__), "tesla-stock-price.csv")}
    Analyse the data and give me the insights
    read_csv to read the file
""")

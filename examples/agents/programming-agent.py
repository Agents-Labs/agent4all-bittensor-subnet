# Importing required classes from the praisonaiagents module
from praisonaiagents import Agent, Tools  # Importing the Agent and Tools classes
# Importing various tools for code manipulation and system commands
from praisonaiagents.tools import execute_code, analyze_code, format_code, lint_code, disassemble_code  # Code Tools
from praisonaiagents.tools import execute_command, list_processes, kill_process, get_system_info  # Shell Tools
from praisonaiagents.tools import duckduckgo  # Web Search Tool

# Creating an instance of the Agent class with specified behavior and tools
agent = Agent(
    instructions="You are a Programming Agent",  # Instructions for the agent's role
    self_reflect=True,  # Enable self-reflection for the agent to evaluate its actions
    min_reflect=5,  # Minimum number of reflections the agent should perform
    max_reflect=10,  # Maximum number of reflections the agent can perform
    tools=[  # List of tools available to the agent
        execute_code,       # Tool to execute code snippets
        analyze_code,       # Tool to analyze the code output
        format_code,        # Tool to format code for readability
        lint_code,          # Tool for linting code to catch errors and improve quality
        disassemble_code,   # Tool to disassemble code into lower-level representations
        execute_command,    # Tool to execute shell commands
        list_processes,     # Tool to list running processes on the system
        kill_process,       # Tool to kill a running process
        get_system_info,    # Tool to retrieve system information
        duckduckgo          # Tool for performing web searches
    ]
)

# Starting the agent with a complex query that describes a series of tasks
agent.start(
    "Write a python script using yfinance to find the stock price of Tesla"  # Task to write a script
    "First check if required packages are installed"  # Step to verify package installation
    "Run it using execute_code"  # Step to execute the script
    "execute_command if you want to run any terminal command"  # Instruction for running terminal commands if needed
    "search internet using duckduckgo if you want to know update python package information"  # Search for package updates if necessary
    "Analyse the output using analyze_code and fix error if required"  # Analyze output and correct errors if any
    "if no package is installed, install it"  # Install necessary packages if they are missing
    "then run the code"  # Final step is to execute the completed code
)

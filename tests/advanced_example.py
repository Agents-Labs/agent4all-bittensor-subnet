from agent4all import Agent4ALL
    
def advanced():
    agent4all = Agent4ALL(
        agent_file="agents.yaml",
        framework="autogen",
    )
    print(agent4all)
    return agent4all.run()

if __name__ == "__main__":
    print(advanced())
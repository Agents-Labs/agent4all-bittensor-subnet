from agent4all import Agent4ALL

def main():
    agent4all = Agent4ALL(agent_file="agents.yaml")
    return agent4all.run()

if __name__ == "__main__":
    print(main())
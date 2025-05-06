from agent4all import Agent4ALL
    
def auto():
    agent4all = Agent4ALL(
        auto="Create a movie script about car in mars",
        framework="autogen"
    )
    print(agent4all.framework)
    return agent4all.run()

if __name__ == "__main__":
    print(auto())
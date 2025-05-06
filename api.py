from flask import Flask
from agent4all import Agent4ALL
import markdown

app = Flask(__name__)

def basic():
    agent4all = Agent4ALL(agent_file="agents.yaml")
    return agent4all.run()

@app.route('/')
def home():
    output = basic()
    html_output = markdown.markdown(output)
    return f'<html><body>{html_output}</body></html>'

if __name__ == "__main__":
    app.run(debug=True)

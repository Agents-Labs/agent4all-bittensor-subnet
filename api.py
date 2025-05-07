from flask import Flask
from praisonai import PraisonAI
import markdown
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

def basic():
    praisonai = PraisonAI(agent_file="agents.yaml")
    return praisonai.run()

@app.route('/')
def home():
    praisonai = PraisonAI(agent_file="agents.yaml")
    output = praisonai.run()
    print(f'Output from basic(): {output}')  # Log the output

    if output is None:
        output = ''

    html_output = markdown.markdown(output)
    return f'<html><body>{html_output}</body></html>'

if __name__ == "__main__":
    app.run(debug=True)
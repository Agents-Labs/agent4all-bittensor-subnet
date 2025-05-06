# tests/test_agents_playbook.py
import unittest
import subprocess
from agent4all import Agent4ALL

class TestAgent4ALLFramework(unittest.TestCase):
    def test_main_with_autogen_framework(self):
        agent4all = Agent4ALL(agent_file='tests/autogen-agents.yaml')
        result = agent4all.run()
        self.assertIn('### Task Output ###', result)

    def test_main_with_custom_framework(self):
        agent4all = Agent4ALL(agent_file='tests/crewai-agents.yaml')
        result = agent4all.run()
        self.assertIn('### Task Output ###', result)

    def test_main_with_internet_search_tool(self):
        agent4all = Agent4ALL(agent_file='tests/search-tool-agents.yaml')
        result = agent4all.run()
        self.assertIn('### Task Output ###', result)

    def test_main_with_built_in_tool(self):
        agent4all = Agent4ALL(agent_file='tests/inbuilt-tool-agents.yaml')
        result = agent4all.run()
        self.assertIn('### Task Output ###', result)
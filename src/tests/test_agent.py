from src.agent.llm_agent import Agent
from src.agent.schemas import AgentInput, AgentOutput

def test_agent_mock_response():
    agent = Agent()
    output = agent.run(AgentInput(user_query="Hello"))
    assert isinstance(output, AgentOutput)
    assert output.summary == "This is a mock response"

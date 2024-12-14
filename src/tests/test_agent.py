from agent.llm_agent import Agent
from agent.schemas import AgentInput, AgentOutput

def test_agent_mock_response():
    agent = Agent()
    output = agent.run(AgentInput(user_query="Hello"))
    assert isinstance(output, AgentOutput)
    assert output.summary == "This is a mock response"

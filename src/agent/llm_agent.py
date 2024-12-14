from .schemas import AgentInput, AgentOutput

class Agent:
    def run(self, agent_input: AgentInput) -> AgentOutput:
        # Mock response for now
        return AgentOutput(summary="This is a mock response", tool_requests=[])

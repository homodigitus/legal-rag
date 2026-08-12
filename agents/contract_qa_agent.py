"""RAG pipeline'ini basit bir agent arayuzune saran ornek agent."""
from __future__ import annotations

from agents.base import AgentResponse, BaseAgent
from rag.pipeline import answer_question


class ContractQAAgent(BaseAgent):
    name = "contract_qa_agent"

    def run(self, input_text: str, **kwargs) -> AgentResponse:
        result = answer_question(input_text)
        return AgentResponse(
            output=result.answer,
            metadata={"sources": result.sources},
        )

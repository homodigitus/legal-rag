"""Minimal agent arayuzu. Framework baglanmadan once basit tutuluyor."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AgentResponse:
    output: str
    metadata: dict


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> AgentResponse:
        raise NotImplementedError

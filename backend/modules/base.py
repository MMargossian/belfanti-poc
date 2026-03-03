from abc import ABC, abstractmethod
from typing import Any


class BaseModule(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Module identifier string (e.g. 'email_intake')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the module."""
        ...

    @abstractmethod
    def get_tools(self) -> list[dict]:
        """Return list of Anthropic tool definitions (JSON schema format)."""
        ...

    @abstractmethod
    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a tool call and return the result."""
        ...

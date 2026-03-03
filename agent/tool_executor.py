"""
Tool executor that routes tool calls to the correct module.

All known module classes are imported here. Modules whose source files
do not yet exist are silently skipped so the system degrades gracefully
as the POC is built out incrementally.
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

from modules.base import BaseModule

logger = logging.getLogger(__name__)

# ── Registry of module classes by (module_path, class_name) ──────────────────
# Each entry is (Python dotted module path, class name inside that module).
# Using lazy imports so that missing module files do not crash the whole app.

_MODULE_REGISTRY: list[tuple[str, str]] = [
    ("modules.email_intake", "EmailIntakeModule"),
    ("modules.quote_extraction", "QuoteExtractionModule"),
    ("modules.tracking", "TrackingModule"),
    ("modules.material_rfq", "MaterialRFQModule"),
    ("modules.quote_preparation", "QuotePreparationModule"),
    ("modules.quickbooks", "QuickBooksModule"),
    ("modules.approval_gates", "ApprovalGatesModule"),
    ("modules.customer_response", "CustomerResponseModule"),
    ("modules.purchase_order", "PurchaseOrderModule"),
    ("modules.work_order", "WorkOrderModule"),
]


def _load_module_instances() -> list[BaseModule]:
    """Attempt to import and instantiate each registered module class.

    Modules whose source file does not yet exist (ImportError / ModuleNotFoundError)
    are logged and skipped so the rest of the system keeps working.
    """
    instances: list[BaseModule] = []
    for dotted_path, class_name in _MODULE_REGISTRY:
        try:
            mod = importlib.import_module(dotted_path)
            cls = getattr(mod, class_name)
            instances.append(cls())
        except (ImportError, ModuleNotFoundError) as exc:
            logger.info(
                "Skipping %s.%s (not yet implemented): %s",
                dotted_path,
                class_name,
                exc,
            )
        except Exception as exc:
            logger.warning(
                "Failed to load %s.%s: %s",
                dotted_path,
                class_name,
                exc,
                exc_info=True,
            )
    return instances


class ToolExecutor:
    """Routes incoming tool calls to the appropriate :class:`BaseModule`."""

    def __init__(self) -> None:
        self.modules: dict[str, BaseModule] = {}
        self._tool_to_module: dict[str, str] = {}
        self._register_all_modules()

    # ── Setup ─────────────────────────────────────────────────────────────

    def _register_all_modules(self) -> None:
        """Load every available module and build the tool -> module lookup."""
        for instance in _load_module_instances():
            self.modules[instance.name] = instance

        # Build reverse map: tool_name -> module_name
        self._tool_to_module = {}
        for mod_name, mod in self.modules.items():
            for tool_def in mod.get_tools():
                tool_name = tool_def["name"]
                if tool_name in self._tool_to_module:
                    logger.warning(
                        "Duplicate tool name '%s' in modules '%s' and '%s'. "
                        "The later registration wins.",
                        tool_name,
                        self._tool_to_module[tool_name],
                        mod_name,
                    )
                self._tool_to_module[tool_name] = mod_name

    # ── Public API ────────────────────────────────────────────────────────

    def get_tools_for_modules(self, enabled_module_names: list[str]) -> list[dict]:
        """Return Anthropic-formatted tool definitions for the given enabled modules.

        Modules that are enabled in the config but whose code is not yet
        implemented are silently skipped (they simply won't appear in the
        tool list sent to Claude).
        """
        tools: list[dict] = []
        for name in enabled_module_names:
            mod = self.modules.get(name)
            if mod is not None:
                tools.extend(mod.get_tools())
        return tools

    def execute(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a single tool call and return its result.

        Raises
        ------
        ValueError
            If *tool_name* does not map to any registered module.
        """
        module_name = self._tool_to_module.get(tool_name)
        if module_name is None:
            raise ValueError(
                f"Unknown tool: '{tool_name}'. "
                f"Registered tools: {sorted(self._tool_to_module.keys())}"
            )

        module = self.modules[module_name]
        return module.execute_tool(tool_name, tool_input)

    # ── Introspection helpers ─────────────────────────────────────────────

    @property
    def registered_module_names(self) -> list[str]:
        """Return sorted list of successfully loaded module names."""
        return sorted(self.modules.keys())

    @property
    def registered_tool_names(self) -> list[str]:
        """Return sorted list of all registered tool names across all modules."""
        return sorted(self._tool_to_module.keys())

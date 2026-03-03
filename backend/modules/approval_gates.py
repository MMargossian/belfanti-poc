"""
Approval Gates module for Phase D of the Belfanti CNC Manufacturing POC.
Provides human-in-the-loop approval checkpoints that signal the orchestrator
to pause and wait for human input via the Streamlit UI.
"""

from typing import Any

from modules.base import BaseModule
from state.store import get_state


class ApprovalGatesModule(BaseModule):
    """Human-in-the-loop approval checkpoints for quote review and final email."""

    @property
    def name(self) -> str:
        return "approval_gates"

    @property
    def description(self) -> str:
        return "Human-in-the-loop approval checkpoints for quote review and final email"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "approval_gate_quote_review",
                "description": (
                    "Request human approval for a quote before sending. "
                    "Pauses the agent loop and presents the quote summary "
                    "to the user for review. Returns a pending_approval status "
                    "that the orchestrator uses to pause execution."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "quote_summary": {
                            "type": "string",
                            "description": "Human-readable summary of the quote.",
                        },
                        "total_amount": {
                            "type": "number",
                            "description": "Total dollar amount of the quote.",
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer.",
                        },
                        "line_items_summary": {
                            "type": "array",
                            "description": "Summary of each line item for display.",
                            "items": {"type": "object"},
                        },
                    },
                    "required": ["quote_summary", "total_amount", "customer_name", "line_items_summary"],
                },
            },
            {
                "name": "approval_gate_email_review",
                "description": (
                    "Request human approval before sending an email with the "
                    "estimate to the customer. Pauses the agent loop and shows "
                    "the email preview for review."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to_email": {
                            "type": "string",
                            "description": "Recipient email address.",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line.",
                        },
                        "body_preview": {
                            "type": "string",
                            "description": "Preview of the email body text.",
                        },
                        "attachments": {
                            "type": "array",
                            "description": "List of attachment filenames or URLs.",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["to_email", "subject", "body_preview"],
                },
            },
            {
                "name": "check_approval_status",
                "description": (
                    "Check the result of a previous approval gate after the "
                    "agent loop resumes. Reads the approval result from "
                    "Streamlit session state."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "gate_name": {
                            "type": "string",
                            "description": "Name of the approval gate to check (e.g. 'quote_review', 'email_review').",
                        },
                    },
                    "required": ["gate_name"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "approval_gate_quote_review":
            return self._gate_quote_review(tool_input)
        elif tool_name == "approval_gate_email_review":
            return self._gate_email_review(tool_input)
        elif tool_name == "check_approval_status":
            return self._check_approval_status(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Tool implementations
    # ------------------------------------------------------------------

    def _gate_quote_review(self, tool_input: dict) -> dict:
        quote_summary = tool_input["quote_summary"]
        total_amount = tool_input["total_amount"]
        customer_name = tool_input["customer_name"]
        line_items_summary = tool_input["line_items_summary"]

        print(
            f"[ApprovalGate] Quote review requested for {customer_name} "
            f"(total: ${total_amount:.2f}) - awaiting human approval"
        )

        return {
            "gate": "quote_review",
            "status": "pending_approval",
            "summary": quote_summary,
            "total": total_amount,
            "customer": customer_name,
            "line_items": line_items_summary,
        }

    def _gate_email_review(self, tool_input: dict) -> dict:
        to_email = tool_input["to_email"]
        subject = tool_input["subject"]
        body_preview = tool_input["body_preview"]
        attachments = tool_input.get("attachments", [])

        print(
            f"[ApprovalGate] Email review requested for {to_email} "
            f"(subject: '{subject}') - awaiting human approval"
        )

        return {
            "gate": "email_review",
            "status": "pending_approval",
            "to": to_email,
            "subject": subject,
            "preview": body_preview,
            "attachments": attachments,
        }

    def _check_approval_status(self, tool_input: dict) -> dict:
        gate_name = tool_input["gate_name"]

        # Read from Streamlit session state
        result = get_state("approval_result")

        if result is None:
            print(f"[ApprovalGate] No approval result found for gate '{gate_name}'")
            return {
                "gate": gate_name,
                "status": "no_result",
                "message": "No approval result found in session state.",
            }

        status = result if isinstance(result, str) else result.get("status", "unknown")

        print(f"[ApprovalGate] Gate '{gate_name}' status: {status}")

        return {
            "gate": gate_name,
            "status": status,
        }

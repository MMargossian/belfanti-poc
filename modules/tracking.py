"""
Tracking module for the Belfanti CNC Manufacturing POC.
Logs RFQ progress to a tracking sheet and stores files in Google Drive.
"""

from datetime import datetime
from typing import Any

from modules.base import BaseModule
from services.mock_google_drive import MockGoogleDriveService
from services.mock_google_sheets import MockGoogleSheetsService


# Module-level singleton services
_sheets = MockGoogleSheetsService()
_drive = MockGoogleDriveService()

# The sheet name used for RFQ tracking
_TRACKING_SHEET = "RFQ Tracker"


class TrackingModule(BaseModule):
    """Log RFQ progress to tracking sheet and store files in Google Drive."""

    @property
    def name(self) -> str:
        return "tracking"

    @property
    def description(self) -> str:
        return "Log RFQ progress to tracking sheet and store files in Google Drive"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "log_to_tracking_sheet",
                "description": (
                    "Append a new row to the RFQ tracking spreadsheet. "
                    "Used when a new RFQ is received and being processed."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rfq_id": {
                            "type": "string",
                            "description": "Unique RFQ identifier (e.g., 'RFQ-2026-0042').",
                        },
                        "customer": {
                            "type": "string",
                            "description": "Customer or company name.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Current status (e.g., 'received', 'quoting', 'quoted', 'accepted').",
                        },
                        "parts_count": {
                            "type": "integer",
                            "description": "Number of parts in the RFQ.",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional notes about the RFQ.",
                        },
                    },
                    "required": ["rfq_id", "customer", "status", "parts_count"],
                },
            },
            {
                "name": "update_tracking_status",
                "description": (
                    "Update the status and details of an existing RFQ in the tracking sheet. "
                    "Finds the row by rfq_id and updates the specified fields."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rfq_id": {
                            "type": "string",
                            "description": "The RFQ identifier to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "New status value.",
                        },
                        "quote_total": {
                            "type": "number",
                            "description": "Total quote amount in dollars (optional).",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes to append (optional).",
                        },
                    },
                    "required": ["rfq_id", "status"],
                },
            },
            {
                "name": "store_cad_files",
                "description": (
                    "Create a Google Drive folder for an RFQ and upload CAD/drawing files to it. "
                    "Returns the folder URL and individual file URLs."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rfq_id": {
                            "type": "string",
                            "description": "RFQ identifier for folder naming.",
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Customer name for folder naming.",
                        },
                        "filenames": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of filenames to upload.",
                        },
                    },
                    "required": ["rfq_id", "customer_name", "filenames"],
                },
            },
            {
                "name": "get_tracking_status",
                "description": (
                    "Look up the current tracking sheet row for an RFQ by its ID. "
                    "Returns the full row data if found."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rfq_id": {
                            "type": "string",
                            "description": "The RFQ identifier to look up.",
                        },
                    },
                    "required": ["rfq_id"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "log_to_tracking_sheet":
            return self._log_to_tracking_sheet(**tool_input)
        elif tool_name == "update_tracking_status":
            return self._update_tracking_status(**tool_input)
        elif tool_name == "store_cad_files":
            return self._store_cad_files(**tool_input)
        elif tool_name == "get_tracking_status":
            return self._get_tracking_status(tool_input["rfq_id"])
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Internal tool implementations
    # ------------------------------------------------------------------

    def _log_to_tracking_sheet(
        self,
        rfq_id: str,
        customer: str,
        status: str,
        parts_count: int,
        notes: str | None = None,
    ) -> dict:
        """Append a new row to the RFQ tracking sheet."""
        row_data = {
            "rfq_id": rfq_id,
            "customer": customer,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": status,
            "parts_count": parts_count,
            "quote_total": "",
            "notes": notes or "",
        }

        result = _sheets.append_row(_TRACKING_SHEET, row_data)
        return result

    def _update_tracking_status(
        self,
        rfq_id: str,
        status: str,
        quote_total: float | None = None,
        notes: str | None = None,
    ) -> dict:
        """Find the row by rfq_id and update its status and optional fields."""
        # First, find the row
        existing_row = _sheets.find_row(_TRACKING_SHEET, "rfq_id", rfq_id)

        if existing_row is None:
            return {
                "status": "not_found",
                "rfq_id": rfq_id,
                "message": f"No tracking row found for RFQ '{rfq_id}'. Use log_to_tracking_sheet first.",
            }

        # Build the updates dict
        updates: dict[str, Any] = {"status": status}
        if quote_total is not None:
            updates["quote_total"] = quote_total
        if notes is not None:
            # Append to existing notes rather than overwriting
            existing_notes = existing_row.get("notes", "")
            if existing_notes:
                updates["notes"] = f"{existing_notes}; {notes}"
            else:
                updates["notes"] = notes

        # We need the internal row number. Re-scan the raw data to find it.
        all_rows = _sheets._sheets.get(_TRACKING_SHEET, [])
        row_number = None
        for row in all_rows:
            if row.get("rfq_id") == rfq_id:
                row_number = row.get("_row_number")
                break

        if row_number is None:
            return {
                "status": "error",
                "rfq_id": rfq_id,
                "message": "Row found but internal row number missing.",
            }

        result = _sheets.update_row(_TRACKING_SHEET, row_number, updates)
        return result

    def _store_cad_files(
        self,
        rfq_id: str,
        customer_name: str,
        filenames: list[str],
    ) -> dict:
        """Create a Drive folder for the RFQ and upload each file."""
        folder_name = f"{rfq_id} - {customer_name}"
        folder_result = _drive.create_folder(folder_name, parent_path="/RFQs")

        folder_id = folder_result["folder_id"]
        folder_url = folder_result["url"]

        uploaded_files: list[dict] = []
        for filename in filenames:
            file_result = _drive.upload_file(filename, folder_id)
            uploaded_files.append({
                "filename": filename,
                "file_id": file_result["file_id"],
                "url": file_result["url"],
            })

        return {
            "folder_name": folder_name,
            "folder_id": folder_id,
            "folder_url": folder_url,
            "files": uploaded_files,
            "files_count": len(uploaded_files),
        }

    def _get_tracking_status(self, rfq_id: str) -> dict:
        """Look up the tracking sheet row for an RFQ."""
        row = _sheets.find_row(_TRACKING_SHEET, "rfq_id", rfq_id)

        if row is None:
            return {
                "found": False,
                "rfq_id": rfq_id,
                "message": f"No tracking entry found for RFQ '{rfq_id}'.",
            }

        return {
            "found": True,
            "rfq_id": rfq_id,
            **row,
        }

"""
Mock Google Sheets service for the Belfanti CNC Manufacturing POC.
Simulates a spreadsheet-backed tracking system with append, update,
get, and find operations. Data stored in-memory per sheet name.

Expected tracking sheet columns:
    rfq_id, customer, date, status, parts_count, quote_total, notes
"""

from datetime import datetime


class MockGoogleSheetsService:
    """Simulates Google Sheets API interactions for job tracking."""

    # Keyed by sheet_name -> list of row dicts.
    # Each row dict also contains a "_row_number" field for internal tracking.
    _sheets: dict[str, list[dict]] = {}

    @classmethod
    def append_row(cls, sheet_name: str, row_data: dict) -> dict:
        """Append a new row to a sheet.

        Args:
            sheet_name: Name of the target sheet (e.g. "RFQ Tracker").
            row_data: Dict of column name -> value pairs.

        Returns:
            Dict with row_number, sheet name, data, and status.
        """
        if sheet_name not in cls._sheets:
            cls._sheets[sheet_name] = []

        row_number = len(cls._sheets[sheet_name]) + 2  # Row 1 is the header
        row = {**row_data, "_row_number": row_number, "_updated_at": datetime.now().isoformat()}
        cls._sheets[sheet_name].append(row)

        print(f"[MockSheets] Row {row_number} appended to '{sheet_name}' -> {_summarize(row_data)}")
        return {
            "row_number": row_number,
            "sheet": sheet_name,
            "data": row_data,
            "status": "appended",
        }

    @classmethod
    def update_row(cls, sheet_name: str, row_number: int, updates: dict) -> dict:
        """Update specific columns in an existing row.

        Args:
            sheet_name: Name of the target sheet.
            row_number: The 1-based row number (2 = first data row).
            updates: Dict of column name -> new value pairs.

        Returns:
            Dict with row_number, sheet name, updates, and status.
        """
        rows = cls._sheets.get(sheet_name, [])
        for row in rows:
            if row.get("_row_number") == row_number:
                row.update(updates)
                row["_updated_at"] = datetime.now().isoformat()
                print(f"[MockSheets] Row {row_number} in '{sheet_name}' updated -> {updates}")
                return {
                    "row_number": row_number,
                    "sheet": sheet_name,
                    "updates": updates,
                    "status": "updated",
                }

        print(f"[MockSheets] Row {row_number} not found in '{sheet_name}'")
        return {
            "row_number": row_number,
            "sheet": sheet_name,
            "updates": updates,
            "status": "not_found",
        }

    @classmethod
    def get_rows(cls, sheet_name: str) -> list[dict]:
        """Return all rows for a given sheet, without internal metadata fields.

        Args:
            sheet_name: Name of the target sheet.

        Returns:
            List of row dicts (internal fields like _row_number stripped).
        """
        rows = cls._sheets.get(sheet_name, [])
        return [_clean_row(r) for r in rows]

    @classmethod
    def find_row(cls, sheet_name: str, column: str, value: str) -> dict | None:
        """Find the first row where a column matches a given value.

        Args:
            sheet_name: Name of the target sheet.
            column: Column name to search.
            value: Value to match (string comparison).

        Returns:
            The matching row dict (cleaned), or None.
        """
        rows = cls._sheets.get(sheet_name, [])
        for row in rows:
            if str(row.get(column, "")) == str(value):
                return _clean_row(row)
        return None

    @classmethod
    def reset(cls) -> None:
        """Clear all stored sheets. Useful for testing."""
        cls._sheets.clear()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _clean_row(row: dict) -> dict:
    """Return a copy of the row without internal metadata keys."""
    return {k: v for k, v in row.items() if not k.startswith("_")}


def _summarize(data: dict) -> str:
    """Create a short summary string of a row for logging."""
    parts = []
    for key in ("rfq_id", "customer", "status"):
        if key in data:
            parts.append(f"{key}={data[key]}")
    if parts:
        return ", ".join(parts)
    # Fallback: show first few keys
    items = list(data.items())[:3]
    return ", ".join(f"{k}={v}" for k, v in items)

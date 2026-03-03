"""
Work Order module for the Belfanti CNC Manufacturing POC.
Creates work orders, packing slips, print PDFs, and Fusion 360 project folders
for manufacturing jobs.
"""

import uuid
from datetime import datetime
from typing import Any

from modules.base import BaseModule
from services.mock_google_drive import MockGoogleDriveService
from services.mock_fusion360 import MockFusion360Service


# Module-level service singletons
_drive = MockGoogleDriveService
_fusion360 = MockFusion360Service

# In-memory work order storage keyed by work_order_id
_work_orders: dict[str, dict] = {}
_work_order_counter: int = 5001


class WorkOrderModule(BaseModule):
    """Create work orders, packing slips, print PDFs, and Fusion 360 project folders."""

    @property
    def name(self) -> str:
        return "work_order"

    @property
    def description(self) -> str:
        return "Create work orders, packing slips, print PDFs, and Fusion 360 project folders"

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "create_work_order",
                "description": (
                    "Create a work order for the shop floor. Specifies the parts to manufacture, "
                    "their materials, and the required machine types."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sales_order_id": {
                            "type": "string",
                            "description": "The sales order this work order fulfills.",
                        },
                        "quote_id": {
                            "type": "string",
                            "description": "The originating quote identifier.",
                        },
                        "parts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "part_number": {"type": "string"},
                                    "part_name": {"type": "string"},
                                    "quantity": {"type": "integer"},
                                    "material": {"type": "string"},
                                    "machine_type": {"type": "string"},
                                },
                            },
                            "description": (
                                "List of parts to manufacture. Each part has part_number, "
                                "part_name, quantity, material, and machine_type."
                            ),
                        },
                    },
                    "required": ["sales_order_id", "quote_id", "parts"],
                },
            },
            {
                "name": "create_packing_slip",
                "description": (
                    "Create a packing slip document for a work order and upload it to "
                    "Google Drive. Lists all parts and quantities for shipping."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "work_order_id": {
                            "type": "string",
                            "description": "The work order this packing slip is for.",
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Customer name for the packing slip header.",
                        },
                        "parts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "part_number": {"type": "string"},
                                    "part_name": {"type": "string"},
                                    "quantity": {"type": "integer"},
                                },
                            },
                            "description": "List of parts with part_number, part_name, and quantity.",
                        },
                        "shipping_address": {
                            "type": "string",
                            "description": "Optional shipping address to include on the slip.",
                        },
                    },
                    "required": ["work_order_id", "customer_name", "parts"],
                },
            },
            {
                "name": "generate_print_pdfs",
                "description": (
                    "Generate shop print PDFs for each part in a work order using Fusion 360. "
                    "Returns a list of PDF URLs for the shop floor."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "work_order_id": {
                            "type": "string",
                            "description": "The work order these prints are for.",
                        },
                        "parts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "part_number": {"type": "string"},
                                    "part_name": {"type": "string"},
                                },
                            },
                            "description": "List of parts with part_number and part_name to generate prints for.",
                        },
                    },
                    "required": ["work_order_id", "parts"],
                },
            },
            {
                "name": "create_fusion360_folder",
                "description": (
                    "Create a Fusion 360 project folder for the job and optionally upload "
                    "CAD files to it. Returns the project URL and any uploaded file URLs."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name for the Fusion 360 project folder.",
                        },
                        "parts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "part_number": {"type": "string"},
                                    "part_name": {"type": "string"},
                                },
                            },
                            "description": "List of parts in the project for reference.",
                        },
                        "cad_files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of CAD filenames to upload to the project.",
                        },
                    },
                    "required": ["project_name", "parts"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "create_work_order":
            return self._create_work_order(**tool_input)
        elif tool_name == "create_packing_slip":
            return self._create_packing_slip(**tool_input)
        elif tool_name == "generate_print_pdfs":
            return self._generate_print_pdfs(**tool_input)
        elif tool_name == "create_fusion360_folder":
            return self._create_fusion360_folder(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # ------------------------------------------------------------------
    # Internal tool implementations
    # ------------------------------------------------------------------

    def _create_work_order(
        self,
        sales_order_id: str,
        quote_id: str,
        parts: list[dict],
    ) -> dict:
        """Create a work order for the shop floor."""
        global _work_order_counter

        work_order_id = f"wo-{uuid.uuid4().hex[:8]}"
        work_order_number = f"WO-{_work_order_counter}"
        _work_order_counter += 1
        created_at = datetime.now().isoformat()

        work_order = {
            "work_order_id": work_order_id,
            "work_order_number": work_order_number,
            "sales_order_id": sales_order_id,
            "quote_id": quote_id,
            "parts": parts,
            "status": "created",
            "created_at": created_at,
        }
        _work_orders[work_order_id] = work_order

        print(f"[WorkOrder] {work_order_number} created for SO {sales_order_id} with {len(parts)} part(s)")

        return {
            "work_order_id": work_order_id,
            "work_order_number": work_order_number,
            "sales_order_id": sales_order_id,
            "quote_id": quote_id,
            "parts": parts,
            "status": "created",
            "created_at": created_at,
        }

    def _create_packing_slip(
        self,
        work_order_id: str,
        customer_name: str,
        parts: list[dict],
        shipping_address: str | None = None,
    ) -> dict:
        """Create a packing slip and upload it to Google Drive."""
        # Build packing slip content
        slip_lines = [
            f"PACKING SLIP",
            f"Work Order: {work_order_id}",
            f"Customer: {customer_name}",
        ]
        if shipping_address:
            slip_lines.append(f"Ship To: {shipping_address}")
        slip_lines.append("")
        slip_lines.append("Parts:")
        for part in parts:
            slip_lines.append(
                f"  - {part.get('part_number', 'N/A')} | "
                f"{part.get('part_name', 'Unknown')} | "
                f"Qty: {part.get('quantity', 1)}"
            )
        slip_content = "\n".join(slip_lines)

        # Create a folder for packing slips if needed, then upload
        folder_result = _drive.create_folder(
            name=f"PackingSlips-{work_order_id}",
            parent_path="/Belfanti/Orders",
        )
        folder_id = folder_result["folder_id"]

        filename = f"packing_slip_{work_order_id}.pdf"
        file_result = _drive.upload_file(
            filename=filename,
            folder_id=folder_id,
            content=slip_content,
        )

        # Update work order if it exists
        if work_order_id in _work_orders:
            _work_orders[work_order_id]["packing_slip_url"] = file_result["url"]

        return {
            "work_order_id": work_order_id,
            "customer_name": customer_name,
            "packing_slip_url": file_result["url"],
            "file_id": file_result["file_id"],
            "filename": filename,
        }

    def _generate_print_pdfs(
        self,
        work_order_id: str,
        parts: list[dict],
    ) -> dict:
        """Generate shop print PDFs for each part via Fusion 360."""
        # Create a project folder for the prints
        project_result = _fusion360.create_project_folder(
            project_name=f"Prints-{work_order_id}",
        )
        project_id = project_result["project_id"]

        pdf_results = []
        for part in parts:
            part_name = part.get("part_name", part.get("part_number", "unknown"))
            pdf_result = _fusion360.generate_print_pdf(
                project_id=project_id,
                part_name=part_name,
            )
            pdf_results.append({
                "part_number": part.get("part_number", ""),
                "part_name": part_name,
                "pdf_url": pdf_result["url"],
                "filename": pdf_result["filename"],
            })

        # Update work order if it exists
        if work_order_id in _work_orders:
            _work_orders[work_order_id]["print_pdf_url"] = project_result["url"]

        print(f"[WorkOrder] Generated {len(pdf_results)} print PDF(s) for {work_order_id}")

        return {
            "work_order_id": work_order_id,
            "project_id": project_id,
            "project_url": project_result["url"],
            "pdfs": pdf_results,
        }

    def _create_fusion360_folder(
        self,
        project_name: str,
        parts: list[dict],
        cad_files: list[str] | None = None,
    ) -> dict:
        """Create a Fusion 360 project folder and upload CAD files."""
        cad_files = cad_files or []

        # Create the project folder
        project_result = _fusion360.create_project_folder(
            project_name=project_name,
        )
        project_id = project_result["project_id"]

        # Upload each CAD file
        uploaded_files = []
        for filename in cad_files:
            file_result = _fusion360.upload_cad_file(
                project_id=project_id,
                filename=filename,
            )
            uploaded_files.append({
                "filename": filename,
                "file_id": file_result["file_id"],
                "url": file_result["url"],
            })

        print(
            f"[WorkOrder] Fusion 360 project '{project_name}' created "
            f"with {len(uploaded_files)} CAD file(s) and {len(parts)} part(s)"
        )

        return {
            "project_name": project_name,
            "project_id": project_id,
            "project_url": project_result["url"],
            "parts": parts,
            "uploaded_files": uploaded_files,
        }

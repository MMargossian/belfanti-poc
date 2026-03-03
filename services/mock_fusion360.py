"""
Mock Fusion 360 service for the Belfanti CNC Manufacturing POC.
Simulates CAD project management, file uploads, and print PDF generation.
All data stored in-memory.
"""

import uuid
from datetime import datetime


class MockFusion360Service:
    """Simulates Autodesk Fusion 360 API interactions."""

    _projects: dict[str, dict] = {}
    _files: dict[str, dict] = {}
    _prints: dict[str, dict] = {}

    @classmethod
    def create_project_folder(cls, project_name: str) -> dict:
        """Create a project folder in mock Fusion 360.

        Args:
            project_name: Name for the project folder.

        Returns:
            Dict with project_id, name, and url.
        """
        project_id = f"f360-proj-{uuid.uuid4().hex[:8]}"
        project = {
            "project_id": project_id,
            "name": project_name,
            "url": f"https://fusion360.mock/projects/{project_id}",
            "files": [],
            "prints": [],
            "created_at": datetime.now().isoformat(),
        }
        cls._projects[project_id] = project

        print(f"[MockFusion360] Project created -> {project_name} ({project_id})")
        return {
            "project_id": project_id,
            "name": project_name,
            "url": f"https://fusion360.mock/projects/{project_id}",
        }

    @classmethod
    def upload_cad_file(cls, project_id: str, filename: str) -> dict:
        """Upload a CAD file to a Fusion 360 project.

        Args:
            project_id: Target project identifier.
            filename: Name of the CAD file (e.g. "bracket_v2.step").

        Returns:
            Dict with file_id, filename, project_id, and url.
        """
        file_id = f"f360-file-{uuid.uuid4().hex[:8]}"
        file_record = {
            "file_id": file_id,
            "filename": filename,
            "project_id": project_id,
            "url": f"https://fusion360.mock/files/{file_id}",
            "uploaded_at": datetime.now().isoformat(),
        }
        cls._files[file_id] = file_record

        # Link to project
        if project_id in cls._projects:
            cls._projects[project_id]["files"].append(file_id)
            project_name = cls._projects[project_id]["name"]
        else:
            project_name = f"(unknown project {project_id})"

        print(f"[MockFusion360] CAD file uploaded -> {filename} to {project_name}")
        return {
            "file_id": file_id,
            "filename": filename,
            "project_id": project_id,
            "url": f"https://fusion360.mock/files/{file_id}",
        }

    @classmethod
    def generate_print_pdf(cls, project_id: str, part_name: str) -> dict:
        """Generate a shop print PDF for a part in a project.

        Args:
            project_id: The project containing the part.
            part_name: Name of the part to generate a print for.

        Returns:
            Dict with pdf_id, filename, and url.
        """
        pdf_id = f"f360-pdf-{uuid.uuid4().hex[:8]}"
        filename = f"{part_name}_print.pdf"

        print_record = {
            "pdf_id": pdf_id,
            "filename": filename,
            "project_id": project_id,
            "part_name": part_name,
            "url": f"https://fusion360.mock/prints/{pdf_id}.pdf",
            "generated_at": datetime.now().isoformat(),
        }
        cls._prints[pdf_id] = print_record

        # Link to project
        if project_id in cls._projects:
            cls._projects[project_id]["prints"].append(pdf_id)

        print(f"[MockFusion360] Print PDF generated -> {filename}")
        return {
            "pdf_id": pdf_id,
            "filename": filename,
            "url": f"https://fusion360.mock/prints/{pdf_id}.pdf",
        }

    @classmethod
    def get_project(cls, project_id: str) -> dict | None:
        """Retrieve a project by ID."""
        return cls._projects.get(project_id)

    @classmethod
    def get_file(cls, file_id: str) -> dict | None:
        """Retrieve a file record by ID."""
        return cls._files.get(file_id)

    @classmethod
    def reset(cls) -> None:
        """Clear all stored data. Useful for testing."""
        cls._projects.clear()
        cls._files.clear()
        cls._prints.clear()

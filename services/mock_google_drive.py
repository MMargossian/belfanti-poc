"""
Mock Google Drive service for the Belfanti CNC Manufacturing POC.
Simulates folder creation, file uploads, and file listing.
All data stored in-memory.
"""

import uuid
from datetime import datetime


class MockGoogleDriveService:
    """Simulates Google Drive API interactions for file/folder management."""

    _folders: dict[str, dict] = {}
    _files: dict[str, dict] = {}

    @classmethod
    def create_folder(cls, name: str, parent_path: str = "/") -> dict:
        """Create a folder in mock Google Drive.

        Args:
            name: Folder name.
            parent_path: Parent folder path (default is root "/").

        Returns:
            Dict with folder_id, name, path, and url.
        """
        folder_id = f"fld-{uuid.uuid4().hex[:8]}"
        # Normalize parent path to avoid double slashes
        parent = parent_path.rstrip("/")
        path = f"{parent}/{name}"

        folder = {
            "folder_id": folder_id,
            "name": name,
            "path": path,
            "url": f"https://drive.mock/folders/{folder_id}",
            "created_at": datetime.now().isoformat(),
            "files": [],
        }
        cls._folders[folder_id] = folder

        print(f"[MockDrive] Folder created -> {path} ({folder_id})")
        return {
            "folder_id": folder_id,
            "name": name,
            "path": path,
            "url": f"https://drive.mock/folders/{folder_id}",
        }

    @classmethod
    def upload_file(
        cls,
        filename: str,
        folder_id: str,
        content: str = "mock file content",
    ) -> dict:
        """Upload a file to a mock Google Drive folder.

        Args:
            filename: Name of the file to upload.
            folder_id: Target folder identifier.
            content: File content (simulated).

        Returns:
            Dict with file_id, filename, folder_id, and url.
        """
        file_id = f"file-{uuid.uuid4().hex[:8]}"

        file_record = {
            "file_id": file_id,
            "filename": filename,
            "folder_id": folder_id,
            "content": content,
            "url": f"https://drive.mock/files/{file_id}",
            "uploaded_at": datetime.now().isoformat(),
        }
        cls._files[file_id] = file_record

        # Link file to its folder
        if folder_id in cls._folders:
            cls._folders[folder_id]["files"].append(file_id)
            folder_name = cls._folders[folder_id]["path"]
        else:
            folder_name = f"(unknown folder {folder_id})"

        print(f"[MockDrive] File uploaded -> {filename} to {folder_name}")
        return {
            "file_id": file_id,
            "filename": filename,
            "folder_id": folder_id,
            "url": f"https://drive.mock/files/{file_id}",
        }

    @classmethod
    def list_files(cls, folder_id: str) -> list[dict]:
        """List all files in a given folder.

        Args:
            folder_id: The folder to list files from.

        Returns:
            List of file dicts (file_id, filename, url, uploaded_at).
        """
        folder = cls._folders.get(folder_id)
        if not folder:
            return []

        result = []
        for fid in folder.get("files", []):
            f = cls._files.get(fid)
            if f:
                result.append({
                    "file_id": f["file_id"],
                    "filename": f["filename"],
                    "url": f["url"],
                    "uploaded_at": f["uploaded_at"],
                })
        return result

    @classmethod
    def get_folder(cls, folder_id: str) -> dict | None:
        """Retrieve a folder by ID."""
        return cls._folders.get(folder_id)

    @classmethod
    def get_file(cls, file_id: str) -> dict | None:
        """Retrieve a file by ID."""
        return cls._files.get(file_id)

    @classmethod
    def reset(cls) -> None:
        """Clear all stored data. Useful for testing."""
        cls._folders.clear()
        cls._files.clear()

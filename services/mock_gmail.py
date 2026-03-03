"""
Mock Gmail service for the Belfanti CNC Manufacturing POC.
Simulates sending and retrieving emails. Stores sent emails in-memory.
"""

import uuid
from datetime import datetime


class MockGmailService:
    """Simulates Gmail API interactions for sending and tracking emails."""

    _emails: dict[str, dict] = {}

    @classmethod
    def send_email(
        cls,
        to: str,
        subject: str,
        body: str,
        attachments: list[str] | None = None,
    ) -> dict:
        """Send a mock email and store it for later retrieval.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body: Email body text.
            attachments: Optional list of attachment filenames.

        Returns:
            Dict with message_id, status, recipient, and subject.
        """
        message_id = f"msg-{uuid.uuid4().hex[:8]}"
        email_record = {
            "message_id": message_id,
            "to": to,
            "subject": subject,
            "body": body,
            "attachments": attachments or [],
            "status": "sent",
            "sent_at": datetime.now().isoformat(),
        }
        cls._emails[message_id] = email_record

        # Log for demo visibility
        print(f"[MockGmail] Email sent -> To: {to}")
        print(f"[MockGmail]   Subject: {subject}")
        if attachments:
            print(f"[MockGmail]   Attachments: {', '.join(attachments)}")
        print(f"[MockGmail]   Message ID: {message_id}")

        return {
            "message_id": message_id,
            "status": "sent",
            "to": to,
            "subject": subject,
        }

    @classmethod
    def get_email(cls, message_id: str) -> dict | None:
        """Retrieve a previously sent email by its message ID.

        Args:
            message_id: The unique message identifier.

        Returns:
            The stored email dict, or None if not found.
        """
        return cls._emails.get(message_id)

    @classmethod
    def get_all_emails(cls) -> list[dict]:
        """Return all sent emails, most recent first."""
        return sorted(
            cls._emails.values(),
            key=lambda e: e["sent_at"],
            reverse=True,
        )

    @classmethod
    def reset(cls) -> None:
        """Clear all stored emails. Useful for testing."""
        cls._emails.clear()

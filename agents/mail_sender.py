from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


class MailSenderAgent:
    def __init__(self) -> None:
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASS")
        self.from_address = os.getenv("FROM_ADDRESS", self.user or "noreply@example.com")

    def send_selection_email(self, recipient_name: str, recipient_email: str, role_text: str, dry_run: bool = True) -> None:
        subject = f"You have been selected for the role: {role_text.splitlines()[0][:50]}"
        body = (
            f"Hello {recipient_name},\n\n"
            "Congratulations! After reviewing resumes, you have been selected as the best fit for the role described below.\n\n"
            f"Role details:\n{role_text}\n\n"
            "Please reply to this message if you are interested in moving forward.\n\n"
            "Best regards,\nCrewAI Hiring Team"
        )
        if dry_run:
            print("--- Dry Run Email ---")
            print(f"To: {recipient_email}")
            print(f"Subject: {subject}")
            print(body)
            print("--- End Dry Run ---")
            return

        if not all([self.host, self.user, self.password]):
            raise RuntimeError("SMTP environment variables are required to send email.")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.from_address
        message["To"] = recipient_email
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port) as smtp:
            smtp.starttls()
            smtp.login(self.user, self.password)
            smtp.send_message(message)

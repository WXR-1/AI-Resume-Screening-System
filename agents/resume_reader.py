from __future__ import annotations

import os
import re
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List

import docx
import pdfplumber


EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
NAME_CANDIDATE_PATTERN = re.compile(r"Name[:\s]+([A-Za-z ,.'-]+)", re.IGNORECASE)


@dataclass
class Resume:
    id: str
    name: str
    email: str
    content: str
    source: str
    score: int = 0
    reasoning: str = ""
    valid: bool = True
    validation_notes: str = ""
    assigned_role: str | None = None


class ResumeReaderAgent:
    @contextmanager
    def _suppress_stderr(self):
        """Temporarily redirect stderr to null to suppress noisy font warnings."""
        with open(os.devnull, "w") as devnull:
            old_stderr_fd = os.dup(2)
            os.dup2(devnull.fileno(), 2)
            old_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
            try:
                yield
            finally:
                sys.stderr.close()
                os.dup2(old_stderr_fd, 2)
                os.close(old_stderr_fd)
                sys.stderr = old_stderr

    def load_resumes(self, resumes_path: Path) -> List[Resume]:
        resumes: List[Resume] = []
        for file_path in sorted(resumes_path.iterdir()):
            if file_path.is_file():
                text = self._extract_text(file_path)
                if not text:
                    continue
                name = self._find_name(text) or file_path.stem
                email = self._find_email(text) or "unknown@example.com"
                resumes.append(
                    Resume(
                        id=file_path.stem,
                        name=name,
                        email=email,
                        content=text,
                        source=str(file_path),
                    )
                )
        return resumes

    def _extract_text(self, file_path: Path) -> str:
        if file_path.suffix.lower() == ".txt":
            return file_path.read_text(encoding="utf-8", errors="ignore")
        if file_path.suffix.lower() == ".pdf":
            return self._extract_pdf(file_path)
        if file_path.suffix.lower() == ".docx":
            return self._extract_docx(file_path)
        return ""

    def _extract_pdf(self, path: Path) -> str:
        text = []
        with self._suppress_stderr():
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text.append(page_text)
        return "\n".join(text)

    def _extract_docx(self, path: Path) -> str:
        doc = docx.Document(path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    def _find_email(self, text: str) -> str | None:
        match = EMAIL_PATTERN.search(text)
        return match.group(0) if match else None

    def _find_name(self, text: str) -> str | None:
        match = NAME_CANDIDATE_PATTERN.search(text)
        if match:
            return match.group(1).strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[0] if lines else None

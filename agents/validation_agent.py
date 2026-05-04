from __future__ import annotations

from typing import List

from agents.llm_client import OllamaLLM
from agents.resume_reader import Resume


class ValidationAgent:
    def __init__(self, llm: OllamaLLM | None = None) -> None:
        self.llm = llm

    def validate_resumes(self, resumes: List[Resume]) -> List[Resume]:
        for resume in resumes:
            self._validate_resume(resume)
        return resumes

    def _validate_resume(self, resume: Resume) -> None:
        notes: list[str] = []
        if not resume.name or resume.name.strip() == "":
            notes.append("Missing candidate name.")
        if not resume.email or resume.email == "unknown@example.com":
            notes.append("Missing or invalid email address.")
        if len(resume.content.strip()) < 100:
            notes.append("Resume content is too short or incomplete.")

        if notes:
            resume.valid = False
            resume.validation_notes = " ".join(notes)
        else:
            resume.valid = True
            resume.validation_notes = "Resume passed basic validation."

from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from agents.llm_client import OllamaLLM
from agents.resume_reader import Resume
from agents.role_matcher import RoleMatcherAgent


@dataclass
class CandidateAssignment:
    resume: Resume
    role: str
    score: int
    reasoning: str


class RoleSelectorAgent:
    def __init__(self, llm: OllamaLLM) -> None:
        self.llm = llm
        self.matcher = RoleMatcherAgent(llm)

    def load_roles(self, role_file: Path) -> List[str]:
        content = role_file.read_text(encoding="utf-8", errors="ignore").strip()
        if not content:
            return []
        sections = re.split(r"\n-{3,}\n|\r?\n\r?\n", content)
        roles = [section.strip() for section in sections if section.strip()]
        return roles

    def assign_roles(self, resumes: List[Resume], roles: List[str]) -> List[CandidateAssignment]:
        assignments: List[CandidateAssignment] = []
        for role in roles:
            candidates = [copy.copy(resume) for resume in resumes]
            scored = self.matcher.score_candidates(candidates, role)
            for resume in scored:
                assignments.append(
                    CandidateAssignment(
                        resume=resume,
                        role=role,
                        score=resume.score,
                        reasoning=resume.reasoning,
                    )
                )
        return assignments

    def choose_best(self, assignments: List[CandidateAssignment]) -> CandidateAssignment:
        if not assignments:
            raise ValueError("No candidate assignments available.")
        return max(assignments, key=lambda assignment: assignment.score)

    def top_assignments(self, assignments: List[CandidateAssignment], limit: int = 5) -> List[CandidateAssignment]:
        """Return the top assignments while avoiding duplicate candidates.

        A candidate may score highly for multiple roles, but the top list
        should show each candidate only once with their best role match.
        """
        sorted_assignments = sorted(assignments, key=lambda assignment: assignment.score, reverse=True)
        unique_assignments: dict[str, CandidateAssignment] = {}
        for assignment in sorted_assignments:
            candidate_key = assignment.resume.id
            if candidate_key not in unique_assignments:
                unique_assignments[candidate_key] = assignment
            if len(unique_assignments) >= limit:
                break
        return list(unique_assignments.values())

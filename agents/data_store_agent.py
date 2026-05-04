from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, List

from agents.role_selector import CandidateAssignment
from agents.resume_reader import Resume


class DataStoreAgent:
    def __init__(self, data_dir: Path | str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def store_potential_candidates(self, resumes: List[Resume]) -> None:
        candidates = [self._serialize_resume(resume) for resume in resumes]
        self._write_json(self.data_dir / "potential_candidates.json", candidates)

    def store_hired_candidate(self, assignment: CandidateAssignment) -> None:
        path = self.data_dir / "hired_candidates.json"
        existing = self._read_json(path)
        existing.append(self._serialize_assignment(assignment))
        self._write_json(path, existing)

    def _serialize_resume(self, resume: Resume) -> dict[str, Any]:
        return {
            "id": resume.id,
            "name": resume.name,
            "email": resume.email,
            "source": resume.source,
            "score": resume.score,
            "role": resume.assigned_role,
            "valid": resume.valid,
            "validation_notes": resume.validation_notes,
            "reasoning": resume.reasoning,
            "stored_at": datetime.utcnow().isoformat() + "Z",
        }

    def _serialize_assignment(self, assignment: CandidateAssignment) -> dict[str, Any]:
        return {
            "id": assignment.resume.id,
            "name": assignment.resume.name,
            "email": assignment.resume.email,
            "role": assignment.role,
            "score": assignment.score,
            "reasoning": assignment.reasoning,
            "source": assignment.resume.source,
            "stored_at": datetime.utcnow().isoformat() + "Z",
        }

    def _write_json(self, path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _read_json(self, path: Path) -> List[Any]:
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

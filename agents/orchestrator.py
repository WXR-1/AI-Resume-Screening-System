from __future__ import annotations

import json
from pathlib import Path
from typing import List

from agents.data_store_agent import DataStoreAgent
from agents.db_store_agent import DBStoreAgent
from agents.llm_client import OllamaLLM
from agents.mail_sender import MailSenderAgent
from agents.resume_reader import Resume, ResumeReaderAgent
from agents.role_selector import CandidateAssignment, RoleSelectorAgent
from agents.role_matcher import RoleMatcherAgent
from agents.validation_agent import ValidationAgent


class OrchestratorAgent:
    def __init__(self, model: str | None = None) -> None:
        self.llm = OllamaLLM(model)
        self.reader = ResumeReaderAgent()
        self.matcher = RoleMatcherAgent(self.llm)
        self.validator = ValidationAgent(self.llm)
        self.role_selector = RoleSelectorAgent(self.llm)
        self.data_store = DataStoreAgent()
        self.db_store = DBStoreAgent()
        self.mailer = MailSenderAgent()

    def run(self, role_file: Path, resumes_path: Path, dry_run: bool = True) -> None:
        resumes = self.reader.load_resumes(resumes_path)
        if not resumes:
            raise SystemExit(f"No resumes found in {resumes_path}")

        print(f"Loaded {len(resumes)} resumes from {resumes_path}")

        roles = self.role_selector.load_roles(role_file)
        if not roles:
            raise SystemExit(f"No roles found in {role_file}")

        validated_resumes = self.validator.validate_resumes(resumes)
        valid_resumes = [resume for resume in validated_resumes if resume.valid]
        invalid_resumes = [resume for resume in validated_resumes if not resume.valid]

        if invalid_resumes:
            print(f"{len(invalid_resumes)} resumes failed validation and will be excluded:")
            for resume in invalid_resumes:
                print(f"- {resume.name} ({resume.email}): {resume.validation_notes}")

        self.data_store.store_potential_candidates(validated_resumes)
        self.db_store.store_potential_candidates(validated_resumes)

        assignments = self.role_selector.assign_roles(valid_resumes, roles)
        if not assignments:
            raise SystemExit("No valid candidate assignments generated.")

        ranked = self.role_selector.top_assignments(assignments, limit=len(assignments))
        self._log_ranked_assignments(ranked)
        best_assignment = ranked[0]
        best_assignment.resume.assigned_role = best_assignment.role

        if self._verify_selection(best_assignment, ranked):
            self.data_store.store_hired_candidate(best_assignment)
            self.db_store.store_hired_candidate(best_assignment)
            self.mailer.send_selection_email(
                recipient_name=best_assignment.resume.name,
                recipient_email=best_assignment.resume.email,
                role_text=best_assignment.role,
                dry_run=dry_run,
            )
        else:
            print("Orchestrator verification failed. Email will not be sent.")
            if not dry_run and self._ask_user_override(best_assignment, ranked):
                self.data_store.store_hired_candidate(best_assignment)
                self.db_store.store_hired_candidate(best_assignment)
                self.mailer.send_selection_email(
                    recipient_name=best_assignment.resume.name,
                    recipient_email=best_assignment.resume.email,
                    role_text=best_assignment.role,
                    dry_run=dry_run,
                )

    def _log_ranked_assignments(self, ranked: List[CandidateAssignment]) -> None:
        print("Top candidate-role matches:")
        for idx, assignment in enumerate(ranked[:5], 1):
            print(
                f"{idx}. {assignment.resume.name} ({assignment.resume.email}) role={assignment.role} score={assignment.score}"
            )

    def _verify_selection(self, best: CandidateAssignment, ranked: List[CandidateAssignment]) -> bool:
        prompt = (
            "You are an orchestration verifier. Confirm whether the top candidate is the best match for the role based on the resume scores and reasoning."
            " If the candidate should not be selected, reply with NO. Otherwise reply with YES and a short validation note.\n\n"
            f"Role:\n{best.role}\n\n"
            f"Top candidate: {best.resume.name} ({best.resume.email}) score={best.score} reasoning={best.reasoning}\n\n"
            "Additional candidates:\n"
        )
        for assignment in ranked[1:4]:
            prompt += f"- {assignment.resume.name} ({assignment.resume.email}) role={assignment.role} score={assignment.score} reasoning={assignment.reasoning[:120]}\n"

        prompt += (
            "\nRespond with valid JSON like:\n"
            '{"decision": "YES", "note": "This candidate is the strongest fit because..."}'
        )
        response = self.llm.generate(prompt)
        decision, note = self._parse_verification_response(response, best, ranked)
        print(f"Orchestration verification: {decision} - {note}")
        return decision

    def _parse_verification_response(self, response: str, best: Resume, ranked: List[Resume]) -> tuple[bool, str]:
        text = response.strip()
        try:
            data = json.loads(text)
            decision = str(data.get("decision", "NO")).strip().upper()
            note = str(data.get("note", "No verification note provided.")).strip()
            return (decision.startswith("Y"), note)
        except json.JSONDecodeError:
            normalized = text.lower()
            if "no" in normalized and "yes" not in normalized:
                return False, text
            if "yes" in normalized:
                return True, text

            if len(ranked) > 1 and best.score - ranked[1].score >= 20:
                return True, "High score margin; selecting top candidate."
            if best.score >= 70:
                return True, "High absolute score; selecting top candidate."
            return False, text or "Unable to parse verification response."

    def _ask_user_override(self, best: CandidateAssignment, ranked: List[CandidateAssignment]) -> bool:
        print(f"\nTop candidate: {best.resume.name} ({best.resume.email}) role={best.role} score={best.score}")
        print(f"Reasoning: {best.reasoning}")
        response = input("Do you want to send the selection email anyway? (y/N): ").strip().lower()
        return response in ("y", "yes")


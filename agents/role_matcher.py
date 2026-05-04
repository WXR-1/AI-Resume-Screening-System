from __future__ import annotations

import json
import re
from typing import List

from agents.llm_client import OllamaLLM
from agents.resume_reader import Resume


class RoleMatcherAgent:
    def __init__(self, llm: OllamaLLM) -> None:
        self.llm = llm
        self._max_llm_candidates = 10

    def score_candidates(self, resumes: List[Resume], role_text: str) -> List[Resume]:
        scored = []
        candidates = self._select_top_candidates(resumes, role_text)
        batch_results = self._evaluate_candidates(candidates, role_text)
        for resume in candidates:
            score, reasoning = batch_results.get(resume.id, (None, None))
            if score is None:
                score, reasoning = self._evaluate_resume(resume, role_text)
            resume.score = score  # type: ignore[attr-defined]
            resume.reasoning = reasoning  # type: ignore[attr-defined]
            scored.append(resume)

        for resume in resumes:
            if resume not in candidates:
                resume.score = 20  # type: ignore[attr-defined]
                resume.reasoning = "Candidate not prioritized for deep scoring."
                scored.append(resume)

        return scored

    def _select_top_candidates(self, resumes: List[Resume], role_text: str) -> List[Resume]:
        if len(resumes) <= self._max_llm_candidates:
            return resumes

        keyword_scores = [
            (resume, self._keyword_match_score(role_text, resume.content))
            for resume in resumes
        ]
        keyword_scores.sort(key=lambda item: item[1], reverse=True)
        return [resume for resume, _ in keyword_scores[: self._max_llm_candidates]]

    def _keyword_match_score(self, role_text: str, resume_text: str) -> int:
        role_tokens = set(self._tokenize_text(role_text))
        resume_tokens = set(self._tokenize_text(resume_text))
        if not role_tokens or not resume_tokens:
            return 0
        overlap = role_tokens.intersection(resume_tokens)
        return int(len(overlap) * 100 / len(role_tokens))

    def _tokenize_text(self, text: str) -> List[str]:
        return [token.lower() for token in re.findall(r"\b[a-zA-Z]{3,}\b", text)]

    def _evaluate_candidates(self, resumes: List[Resume], role_text: str) -> dict[str, tuple[int, str]]:
        prompt = (
            "You are an expert recruiter. Evaluate each candidate resume below against the target role description.\n"
            "For each candidate, provide a score from 0 to 100 and a short explanation of their fit.\n"
            "Respond only with valid JSON: a list of objects with keys id, score, and reasoning.\n\n"
            "Role description:\n" + role_text + "\n\n"
            "Candidates:\n"
        )
        for resume in resumes:
            prompt += f"- id: {resume.id}\n  name: {resume.name}\n  resume_content: {resume.content}\n\n"

        response = self.llm.generate(prompt)
        parsed = self._parse_batch_response(response)
        if parsed:
            return parsed

        # Fallback to individual evaluation if batch parse fails
        results: dict[str, tuple[int, str]] = {}
        for resume in resumes:
            results[resume.id] = self._evaluate_resume(resume, role_text)
        return results

    def _evaluate_resume(self, resume: Resume, role_text: str) -> tuple[int, str]:
        prompt = (
            "You are an expert recruiter. Evaluate the candidate resume against the target role description.\n"
            "Provide a score from 0 to 100 and a short explanation of the candidate's fit.\n"
            "Score higher for strong alignment with required skills, experience, and role responsibilities.\n"
            "If the resume is missing relevant experience, score it lower.\n\n"
            "Role description:\n" + role_text + "\n\n"
            "Resume content:\n" + resume.content + "\n\n"
            "Respond only with valid JSON like this:\n"
            '{"score": 78, "reasoning": "Strong Python and ML background, but limited production sys experience."}'
        )
        response = self.llm.generate(prompt)
        return self._parse_response(response)

    def _parse_batch_response(self, text: str) -> dict[str, tuple[int, str]]:
        text = text.strip()
        data = self._extract_json(text)
        if data is None or not isinstance(data, list):
            return {}

        results: dict[str, tuple[int, str]] = {}
        for item in data:
            if not isinstance(item, dict) or "id" not in item:
                continue
            try:
                score = int(item.get("score", 50))
            except (ValueError, TypeError):
                score = 50
            reasoning = str(item.get("reasoning", "No reasoning provided.")).strip()
            results[str(item["id"])] = (max(0, min(100, score)), reasoning)
        return results

    def _parse_response(self, text: str) -> tuple[int, str]:
        text = text.strip()
        data = self._extract_json(text)
        if isinstance(data, dict):
            try:
                score = int(data.get("score", 50))
            except (ValueError, TypeError):
                score = 50
            reasoning = str(data.get("reasoning", "No reasoning provided.")).strip()
            return max(0, min(100, score)), reasoning

        # fallback parse from text if JSON is not returned
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        score = 50
        for line in lines:
            if "score" in line.lower():
                digits = [int(x) for x in line.split() if x.isdigit()]
                if digits:
                    score = max(0, min(100, digits[0]))
                    break
        reasoning = " ".join(line for line in lines if "score" not in line)
        return score, reasoning or text

    def _extract_json(self, text: str):
        text = text.strip()
        if not text:
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        for start in (text.find("["), text.find("{")):
            if start == -1:
                continue
            try:
                return json.loads(text[start:])
            except json.JSONDecodeError:
                continue
        return None

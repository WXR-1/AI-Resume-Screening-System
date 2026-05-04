from __future__ import annotations

from typing import List

from agents.llm_client import OllamaLLM
from agents.resume_reader import Resume


class CandidateRankerAgent:
    def __init__(self, llm: OllamaLLM) -> None:
        self.llm = llm

    def rank_candidates(self, resumes: List[Resume], role_text: str) -> List[Resume]:
        ranked = sorted(resumes, key=lambda resume: getattr(resume, "score", 0), reverse=True)
        if ranked and getattr(ranked[0], "score", 0) == getattr(ranked[-1], "score", 0):
            ranked = self._break_tie(ranked, role_text)
        return self._verify_ranking(ranked, role_text)

    def _break_tie(self, ranked: List[Resume], role_text: str) -> List[Resume]:
        prompt = (
            "You are an expert recruiter. The candidates below all scored equally on an initial pass."
            " Choose which candidate is the best fit for the role based on resume details and provide a ranked order.\n\n"
            "Role:\n" + role_text + "\n\n"
            "Candidates:\n"
        )
        for resume in ranked:
            prompt += f"- {resume.name} ({resume.email}) score={getattr(resume, 'score', 0)} reasoning={getattr(resume, 'reasoning', '')[:140]}\n"
        prompt += "\nRespond with the candidate names in order of best fit, one per line."
        response = self.llm.generate(prompt)
        ordered_names = [line.strip() for line in response.splitlines() if line.strip()]
        name_to_resume = {resume.name: resume for resume in ranked}
        ordered = [name_to_resume[name] for name in ordered_names if name in name_to_resume]
        if len(ordered) == len(ranked):
            return ordered
        return ranked

    def _verify_ranking(self, ranked: List[Resume], role_text: str) -> List[Resume]:
        if not ranked:
            return ranked

        top_three = ranked[:3]
        prompt = (
            "You are a validation agent. Confirm that the selected candidates are ordered by fit to the role."
            " If the order is wrong, suggest which candidate should be first.\n\n"
            "Role:\n" + role_text + "\n\n"
            "Candidates:\n"
        )
        for resume in top_three:
            prompt += f"- {resume.name} ({resume.email}) score={getattr(resume, 'score', 0)} reasoning={getattr(resume, 'reasoning', '')[:120]}\n"
        prompt += "\nAnswer with the recommended top candidate name and a short justification."
        response = self.llm.generate(prompt)

        if top_three and top_three[0].name not in response:
            # fallback: keep original order if verification is ambiguous
            pass
        return ranked

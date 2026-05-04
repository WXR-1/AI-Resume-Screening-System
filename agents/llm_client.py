from __future__ import annotations

import os
import subprocess
from typing import Optional

import requests


class OllamaLLM:
    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.use_api = os.getenv("OLLAMA_USE_API", "true").lower() not in {"false", "0", "no"}

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        if self.use_api:
            try:
                return self._generate_via_api(prompt, max_tokens, temperature)
            except Exception as exc:
                print(f"Warning: Ollama API unavailable, falling back to CLI: {exc}")

        return self._generate_via_cli(prompt, max_tokens, temperature)

    def _generate_via_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=15)
        if response.status_code != 200:
            raise RuntimeError(f"ollama API failed: {response.status_code} {response.text}")
        data = response.json()
        return data.get("response", "").strip()

    def _generate_via_cli(self, prompt: str, max_tokens: int, temperature: float) -> str:
        command = ["ollama", "run", self.model]
        result = subprocess.run(command, input=prompt, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"ollama CLI failed: {result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
            )
        return result.stdout.strip()

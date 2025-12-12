from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# Provider: Groq (https://console.groq.com/)
try:
    from groq import Groq
except Exception:
    Groq = None

LABEL_RE = re.compile(r"\b(attacker|genuine)\b", re.IGNORECASE)

def extract_label(text: str) -> str:
    if not text:
        return "unknown"
    m = LABEL_RE.search(text.strip())
    if not m:
        return "unknown"
    return m.group(1).lower()

@dataclass
class LLMResponse:
    text: str
    raw: Any

class LLMClient:
    def generate(self, prompt: str) -> LLMResponse:
        raise NotImplementedError

class GroqClient(LLMClient):
    def __init__(self, model: str, temperature: float = 0.0, max_tokens: int = 16):
        if Groq is None:
            raise ImportError("groq package not installed. Run: pip install groq")
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY is not set. Set it as an environment variable.")
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = float(temperature)
        self.max_tokens = int(max_tokens)

    def generate(self, prompt: str) -> LLMResponse:
        # Chat-style completion
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise classifier. Output only the final label."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        text = resp.choices[0].message.content if resp and resp.choices else ""
        return LLMResponse(text=text or "", raw=resp)

def build_client(provider: str, model: str, temperature: float = 0.0, max_tokens: int = 16) -> LLMClient:
    provider = provider.lower().strip()
    if provider == "groq":
        return GroqClient(model=model, temperature=temperature, max_tokens=max_tokens)
    raise ValueError(f"Unsupported provider: {provider}. Supported: groq")

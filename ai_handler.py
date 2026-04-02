"""
AI Handler Module
=================
Handles communication with Ollama (local AI) for MCQ solving.
Includes caching, error handling, and optimized prompts.

Ollama provides run locally - download from https://ollama.ai
"""

import requests
import hashlib
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
import time


@dataclass
class MCQAnswer:
    """Represents an MCQ answer from the AI."""
    answer: str  # A, B, C, or D
    explanation: str
    success: bool
    error_message: str = ""


class AIHandler:
    """
    Handles AI interactions for MCQ solving using Ollama (local AI).
    Optimized for speed with caching and efficient prompts.
    """

    # Optimized system prompt for fast, accurate MCQ solving
    SYSTEM_PROMPT = """You are an expert MCQ solver. Analyze the question and options carefully.

RULES:
1. Identify the correct answer (A, B, C, or D)
2. Provide a 1-sentence explanation
3. Be confident and direct
4. If text is unclear, make your best educated guess

FORMAT YOUR RESPONSE EXACTLY AS:
ANSWER: [letter]
EXPLANATION: [one sentence]"""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "mistral"):
        """
        Initialize the AI handler for Ollama.

        Args:
            ollama_url: URL where Ollama is running (default: localhost:11434)
            model: Model to use (default: mistral - fast and free)
                   Other options: llama2, neural-chat, orca-mini
        """
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self._cache: Dict[str, MCQAnswer] = {}
        self._cache_max_size = 100
        self._verified = False

    def verify_connection(self) -> bool:
        """
        Verify that Ollama is running and the model is available.

        Returns:
            True if connection successful, False otherwise
        """
        if self._verified:
            return True

        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                self._verified = True
                return True
            return False
        except Exception:
            return False

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.md5(text.encode()).hexdigest()

    def _parse_response(self, response_text: str) -> Tuple[str, str]:
        """
        Parse the AI response to extract answer and explanation.

        Args:
            response_text: Raw response from AI

        Returns:
            Tuple of (answer_letter, explanation)
        """
        lines = response_text.strip().split('\n')
        answer = ""
        explanation = ""

        for line in lines:
            line = line.strip()
            if line.upper().startswith("ANSWER:"):
                # Extract just the letter
                answer_part = line.split(":", 1)[1].strip()
                # Get first letter that is A, B, C, or D
                for char in answer_part.upper():
                    if char in "ABCD":
                        answer = char
                        break
            elif line.upper().startswith("EXPLANATION:"):
                explanation = line.split(":", 1)[1].strip()

        # Fallback: try to find answer letter anywhere
        if not answer:
            for char in response_text.upper():
                if char in "ABCD":
                    answer = char
                    break

        return answer, explanation

    def solve_mcq(self, mcq_text: str) -> MCQAnswer:
        """
        Send MCQ text to Ollama and get the answer.

        Args:
            mcq_text: The MCQ question and options text

        Returns:
            MCQAnswer with the result
        """
        # Check cache first
        cache_key = self._get_cache_key(mcq_text)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Validate input
        if not mcq_text or len(mcq_text.strip()) < 10:
            return MCQAnswer(
                answer="",
                explanation="",
                success=False,
                error_message="Text too short or empty. Please select a valid MCQ."
            )

        # Verify connection if not yet verified
        if not self._verified:
            if not self.verify_connection():
                return MCQAnswer(
                    answer="",
                    explanation="",
                    success=False,
                    error_message="Ollama not running. Start Ollama first (ollama serve)"
                )

        try:
            # Make API call to Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{self.SYSTEM_PROMPT}\n\nSolve this MCQ:\n\n{mcq_text}",
                    "stream": False,
                    "temperature": 0.3,  # Lower temperature for consistent answers
                },
                timeout=60
            )

            if response.status_code != 200:
                return MCQAnswer(
                    answer="",
                    explanation="",
                    success=False,
                    error_message=f"Ollama error: {response.status_code}"
                )

            # Extract response text
            response_data = response.json()
            response_text = response_data.get("response", "")

            # Parse answer and explanation
            answer, explanation = self._parse_response(response_text)

            if not answer:
                return MCQAnswer(
                    answer="?",
                    explanation="Could not determine the answer from the text.",
                    success=False,
                    error_message="Failed to parse answer"
                )

            result = MCQAnswer(
                answer=answer,
                explanation=explanation or "Based on the given options.",
                success=True
            )

            # Cache the result
            self._add_to_cache(cache_key, result)

            return result

        except requests.exceptions.ConnectionError:
            return MCQAnswer(
                answer="",
                explanation="",
                success=False,
                error_message="Cannot connect to Ollama. Is it running?"
            )
        except requests.exceptions.Timeout:
            return MCQAnswer(
                answer="",
                explanation="",
                success=False,
                error_message="Ollama request timed out. Try again."
            )
        except Exception as e:
            return MCQAnswer(
                answer="",
                explanation="",
                success=False,
                error_message=f"Error: {str(e)}"
            )

    def _add_to_cache(self, key: str, value: MCQAnswer):
        """Add result to cache with size limit."""
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry (first key)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = value

    def clear_cache(self):
        """Clear the response cache."""
        self._cache.clear()


# Singleton instance
_ai_instance: Optional[AIHandler] = None


def get_ai_handler(ollama_url: str = "http://localhost:11434", model: str = "mistral") -> AIHandler:
    """
    Get or create the singleton AIHandler instance.

    Args:
        ollama_url: Ollama server URL
        model: Model name to use

    Returns:
        AIHandler instance
    """
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = AIHandler(ollama_url=ollama_url, model=model)
    return _ai_instance

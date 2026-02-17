"""OpenAI wrapper for location extraction."""

import logging
import os
import re
from dataclasses import dataclass

from openai import OpenAI

logger = logging.getLogger(__name__)


def get_openai_api_key() -> str:
    """Get OpenAI API key from environment.

    Returns:
        API key string

    Raises:
        ValueError: If no API key is found
    """
    if key := os.environ.get("OPENAI_API_KEY"):
        return key

    raise ValueError(
        "No OpenAI API key found. Set OPENAI_API_KEY environment variable."
    )


@dataclass
class LocationPrediction:
    """Result of LLM location extraction."""

    extracted_location: str | None
    confidence_score: float
    model_name: str = "gpt-4o-mini"
    explanation: str | None = None
    granularity: str | None = None


@dataclass
class LLMLocationExtractor:
    """Wrapper for OpenAI location extraction calls."""

    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 500
    country: str = "US"

    def __post_init__(self) -> None:
        api_key = get_openai_api_key()
        self._client = OpenAI(api_key=api_key)

    def _build_prompt(self, job_description: str) -> str:
        return f"""You are an information extraction assistant. Extract the most specific primary work location explicitly mentioned in the job posting. Only copy text that exists in the context; do not infer, normalize, or reformat.

Context:
{job_description}

Question:
What is the primary work location for this job?

Extraction rules (strict):
- Prefer the most specific location by this order:
  1) full street address including suite/building and postal code
  2) city, state, postal code
  3) city, state
  4) city only
  5) state only
  6) country only
- If a full street address appears anywhere in the posting, return that entire address exactly as written.
- Prefer locations explicitly labeled with "Location:", "Work Location", "Primary Location", "Office", "Site" near the role header.
- If multiple candidates exist at the same granularity, choose the one most clearly tied to the job's work location.
- Do not invent missing parts. If no higher-granularity location exists, fall back to the next level.
- Exclude emails, phone numbers, URLs, and HR or corporate mailing blocks not tied to the job location.

Response format (JSON only):
- Return JSON only (no prose, no markdown).
- Use exactly this object and do not add extra keys:
{{
  "explanation": string,
  "granularity": "full_street" | "city_state_postal" | "city_state" | "city" | "state" | "country" | "none",
  "answer": string
}}
- If no location is present, set "granularity" to "none" and "answer" to "UNKNOWN".
"""

    def _parse_response(self, response_text: str) -> tuple[str | None, str | None, str | None]:
        """Parse JSON response to extract answer, explanation, and granularity."""
        import json
        
        try:
            # Handle potential markdown code blocks
            text = response_text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\n?", "", text)
                text = re.sub(r"\n?```$", "", text)
            
            data = json.loads(text)
            
            answer = data.get("answer")
            if answer and answer.upper() == "UNKNOWN":
                answer = None
                
            explanation = data.get("explanation")
            granularity = data.get("granularity")
            
            return answer, explanation, granularity
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response: %s", response_text[:200])
            return None, None, None

    def _calculate_confidence(
        self, answer: str | None, explanation: str | None, granularity: str | None
    ) -> float:
        """Calculate confidence score based on response quality."""
        if answer is None:
            return 0.0

        score = 0.5

        if explanation and len(explanation) > 20:
            score += 0.2

        granularity_scores = {
            "full_street": 0.3,
            "city_state_postal": 0.28,
            "city_state": 0.25,
            "city": 0.2,
            "state": 0.15,
            "country": 0.1,
            "none": 0.0,
        }
        score += granularity_scores.get(granularity or "none", 0.0)

        return min(score, 1.0)

    def extract_location(self, job_description: str) -> LocationPrediction:
        """Extract work location from job description using LLM.

        Args:
            job_description: The job posting text to analyze

        Returns:
            LocationPrediction with extracted location and metadata
        """
        prompt = self._build_prompt(job_description)
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            response_text = response.choices[0].message.content
            answer, explanation, granularity = self._parse_response(response_text)
            confidence = self._calculate_confidence(answer, explanation, granularity)

            return LocationPrediction(
                extracted_location=answer,
                confidence_score=confidence,
                model_name=self.model,
                explanation=explanation,
                granularity=granularity,
            )

        except Exception as e:
            logger.exception("OpenAI API error")
            return LocationPrediction(
                extracted_location=None,
                confidence_score=0.0,
                model_name=self.model,
                explanation=f"API error: {str(e)}",
                granularity="none",
            )

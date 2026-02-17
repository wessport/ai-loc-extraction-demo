import json
import re
from dataclasses import dataclass
from openai import OpenAI

from .prompts import EXTRACTION_PROMPT


@dataclass
class ExtractionResult:
    answer: str
    granularity: str
    explanation: str
    is_remote: bool
    remote_indicators: list[str]


REMOTE_PATTERNS = [
    r"\bremote\b",
    r"\bwork from home\b",
    r"\bwfh\b",
    r"\btelecommute\b",
    r"\btelework\b",
    r"\bhybrid\b",
    r"\bvirtual position\b",
    r"\bfully distributed\b",
]


def detect_remote_indicators(text: str) -> list[str]:
    """Detect remote/hybrid work indicators in text."""
    text_lower = text.lower()
    found = []
    for pattern in REMOTE_PATTERNS:
        matches = re.findall(pattern, text_lower)
        found.extend(matches)
    return list(set(found))


def extract_location(text: str, client: OpenAI, model: str = "gpt-4o-mini") -> ExtractionResult:
    """
    Extract location from job posting text using an LLM.
    
    Args:
        text: The job posting text to analyze
        client: OpenAI client instance
        model: Model to use for extraction
        
    Returns:
        ExtractionResult with location data
    """
    prompt = EXTRACTION_PROMPT.format(context=text)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=500,
    )
    
    raw_content = response.choices[0].message.content.strip()
    
    # Parse JSON response
    try:
        # Handle potential markdown code blocks
        if raw_content.startswith("```"):
            raw_content = re.sub(r"^```(?:json)?\n?", "", raw_content)
            raw_content = re.sub(r"\n?```$", "", raw_content)
        
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        data = {
            "answer": "PARSE_ERROR",
            "granularity": "none",
            "explanation": f"Failed to parse LLM response: {raw_content[:200]}"
        }
    
    # Detect remote indicators
    remote_indicators = detect_remote_indicators(text)
    
    return ExtractionResult(
        answer=data.get("answer", "UNKNOWN"),
        granularity=data.get("granularity", "none"),
        explanation=data.get("explanation", ""),
        is_remote=len(remote_indicators) > 0,
        remote_indicators=remote_indicators,
    )

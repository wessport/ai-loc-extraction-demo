EXTRACTION_PROMPT = """You are an information extraction assistant. Extract the most specific primary work location explicitly mentioned in the job posting. Only copy text that exists in the context; do not infer, normalize, or reformat.

Context:
{context}

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
- If a full street address appears anywhere in the posting, return that entire address (including suite/floor/building, punctuation, abbreviations, and ZIP/postal code) exactly as written.
- When the location line uses a label + dash pattern (e.g., "Location: [site name] - [address] (qualifier)"), return only the address after the dash and exclude any trailing parenthetical qualifiers like "(Hybrid)".
- When a street address is present, capture the contiguous span from the street number through the postal code, inclusive. Do not drop leading street name/number segments or suite/building designators.
- If a venue/site/facility/organization name appears adjacent to an address (e.g., "[Venue] - 123 Main St..." or "[Venue], 123 Main St..."), exclude the venue name and return only the address portion beginning at the first street number.
- Treat separators such as "-", "–", "—", ":", and "," as potential dividers between a venue name and the address; always capture from the first street number through the postal code.
- Terminate the span at the end of the postal/ZIP code; if a country name immediately follows, include the country name, but exclude any parenthetical country codes (e.g., "(US)").
- Do not consider venue-only or unit-only mentions without a street name (e.g."#5 Woodfield Shopping Center") as a full street address; when no street name is present, fall back to the next granularity (e.g., city, state, postal).
- Prefer locations explicitly labeled with "Location:", "Work Location", "Primary Location", "Office", "Site" near the role header over addresses in footer/contact sections.
- If multiple candidates exist at the same granularity, choose the one most clearly tied to the job's work location (by label or proximity to the job title/overview).
- Do not invent missing parts. If no higher-granularity location exists, fall back to the next level in the order above.
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

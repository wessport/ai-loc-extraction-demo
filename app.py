#!/usr/bin/env python3
"""
AI Location Extraction Demo - Flask Application

A Flask-based web app for demonstrating AI-powered location extraction
from job descriptions using OpenAI's GPT-4o-mini.

Author: Wes Porter
"""

import json
import logging
import os
import time

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from utils.llm_extractor import LLMLocationExtractor

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    """Serve the main visualization page."""
    return send_from_directory("static", "index.html")


@app.route("/static/<path:path>")
def serve_static(path):
    """Serve static files with proper MIME types."""
    mime_types = {
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".ico": "image/x-icon",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
    }
    
    ext = os.path.splitext(path)[1].lower()
    mimetype = mime_types.get(ext)
    
    return send_from_directory("static", path, mimetype=mimetype)


@app.route("/api/extract", methods=["POST"])
def extract_location():
    """
    Extract location from job description using LLM.

    Request body:
        {
            "job_description": "Full job description text...",
            "country": "US"  // Optional, defaults to US
        }

    Response:
        {
            "success": true,
            "location": "123 Main St, Austin, TX 78701",
            "granularity": "full_street",
            "explanation": "The job posting explicitly mentions...",
            "confidence": 0.85,
            "model": "gpt-4o-mini",
            "processing_steps": [...]
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        job_description = data.get("job_description", "").strip()
        country = data.get("country", "US").upper()

        if not job_description:
            return jsonify({"success": False, "error": "job_description is required"}), 400

        steps = []

        # Step 1: Parse input
        step_start = time.time()
        char_count = len(job_description)
        word_count = len(job_description.split())
        steps.append({
            "step": "parsing",
            "description": f"Parsed {word_count} words ({char_count} characters)",
            "duration_ms": int((time.time() - step_start) * 1000),
        })

        # Step 2: Initialize extractor
        step_start = time.time()
        try:
            extractor = LLMLocationExtractor(country=country)
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 500

        steps.append({
            "step": "initialization",
            "description": f"Loaded {country} extraction model",
            "duration_ms": int((time.time() - step_start) * 1000),
        })

        # Step 3: LLM Inference
        step_start = time.time()
        result = extractor.extract_location(job_description)
        inference_time = int((time.time() - step_start) * 1000)
        steps.append({
            "step": "llm_inference",
            "description": "GPT-4o-mini analyzed job description",
            "duration_ms": inference_time,
        })

        # Step 4: Validation
        step_start = time.time()
        location = result.extracted_location
        is_valid = location is not None and location.upper() != "UNKNOWN"
        steps.append({
            "step": "validation",
            "description": f"Location {'found' if is_valid else 'not found'}",
            "duration_ms": int((time.time() - step_start) * 1000),
        })

        # Find location position in text for highlighting
        location_start = -1
        location_end = -1
        if location:
            location_start = job_description.find(location)
            if location_start >= 0:
                location_end = location_start + len(location)
            else:
                lower_desc = job_description.lower()
                lower_loc = location.lower()
                location_start = lower_desc.find(lower_loc)
                if location_start >= 0:
                    location_end = location_start + len(location)

        return jsonify({
            "success": True,
            "location": location,
            "granularity": result.granularity,
            "explanation": result.explanation,
            "confidence": result.confidence_score,
            "model": result.model_name,
            "processing_steps": steps,
            "highlight": {
                "start": location_start,
                "end": location_end,
            } if location_start >= 0 else None,
        })

    except Exception as e:
        logger.exception("Error during extraction")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "ai-loc-extraction-demo",
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    logger.info(f"Starting AI Location Extraction Demo on port {port}")
    logger.info(f"Open http://localhost:{port} in your browser")
    app.run(host="0.0.0.0", port=port, debug=True)

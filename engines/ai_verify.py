"""
AI Document Verification Engine
Uses OCR.space API (works on Render) + Groq LLM for analysis
"""
import os
import json
import requests
import base64
from datetime import datetime

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False


OCR_API_KEY = os.getenv('OCR_SPACE_API_KEY', 'K83987123488957')  # fallback free key
OCR_API_URL = 'https://api.ocr.space/parse/image'


def extract_text(file_path):
    """Extract text using OCR.space API."""
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                OCR_API_URL,
                files={'file': f},
                data={
                    'apikey': OCR_API_KEY,
                    'language': 'eng',
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'scale': True,
                    'OCREngine': 2,
                },
                timeout=60
            )

        if response.status_code != 200:
            return {"error": f"OCR API returned {response.status_code}"}

        data = response.json()

        if data.get('IsErroredOnProcessing'):
            err = data.get('ErrorMessage', ['Unknown OCR error'])
            return {"error": str(err)}

        parsed_results = data.get('ParsedResults', [])
        if not parsed_results:
            return {"error": "No text found in document"}

        text = parsed_results[0].get('ParsedText', '').strip()
        if not text or len(text) < 20:
            return {"error": "Document mein readable text nahi mila. Clear scan upload karo."}

        return {"text": text, "pages": len(parsed_results)}

    except requests.exceptions.Timeout:
        return {"error": "OCR API timeout — 60 second mein response nahi aaya"}
    except Exception as e:
        return {"error": f"OCR error: {str(e)}"}


def ai_analyze(text, doc_type, student_name=None):
    """Send extracted text to Groq for structured analysis."""
    if not GROQ_AVAILABLE:
        return {"error": "Groq not available"}

    api_key = os.getenv('GROQ_API_KEY', '')
    if not api_key:
        return {"error": "GROQ_API_KEY not set"}

    client = Groq(api_key=api_key)

    prompt = f"""You are an expert document verification assistant for a study-abroad education platform.

Document Type Expected: {doc_type}
Expected Student Name (from profile): {student_name or 'Not provided'}

Text extracted from the document via OCR:
---
{text[:4000]}
---

Analyze this document and return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:

{{
  "document_type_detected": "Passport/Marksheet/IELTS/Degree/SOP/Bank Statement/Other",
  "confidence": 0-100,
  "extracted_fields": {{
    "name": "extracted full name or null",
    "dob": "date of birth or null",
    "document_number": "passport/roll/TRF number or null",
    "issue_date": "issue date or null",
    "expiry_date": "expiry date or null",
    "institution": "school/university name or null",
    "score_or_marks": "score/marks if applicable or null"
  }},
  "cross_checks": {{
    "name_matches_profile": true/false/null,
    "dob_present": true/false,
    "expiry_valid": true/false/null,
    "format_looks_correct": true/false
  }},
  "anomalies": ["list of any suspicious findings"],
  "risk_score": 0-100,
  "verdict": "PASS/FLAG/REVIEW",
  "recommendation": "brief recommendation in simple English"
}}

Be conservative. If unsure, set verdict to REVIEW. Never claim 100% authenticity."""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500,
        )
        content = response.choices[0].message.content.strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        return json.loads(content)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON from AI: {str(e)}", "raw": content[:500]}
    except Exception as e:
        return {"error": str(e)}


class AIVerifyEngine:
    @staticmethod
    def verify_document(file_path, doc_type, student_name=None):
        """Main verification pipeline."""
        ocr = extract_text(file_path)
        if "error" in ocr:
            return {
                "status": "error",
                "stage": "ocr",
                "message": ocr["error"],
            }

        text = ocr.get("text", "")
        analysis = ai_analyze(text, doc_type, student_name)
        if "error" in analysis:
            return {
                "status": "error",
                "stage": "ai",
                "message": analysis["error"],
                "raw_text": text[:300],
            }

        return {
            "status": "ok",
            "text_preview": text[:500],
            "analysis": analysis,
            "verified_at": datetime.utcnow().isoformat(),
        }


ai_verify = AIVerifyEngine()
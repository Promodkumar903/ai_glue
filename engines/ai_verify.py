"""
AI Document Verification Engine
Uses Tesseract OCR + Groq LLM to extract fields and flag anomalies
"""
import os
import json
import base64
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False


def extract_text(file_path):
    """Extract text from image or PDF using Tesseract."""
    if not OCR_AVAILABLE:
        return {"error": "Tesseract not installed"}
    try:
        if file_path.lower().endswith('.pdf'):
            from pdf2image import convert_from_path
            pages = convert_from_path(file_path, dpi=200)
            text = ""
            for page in pages[:3]:
                text += pytesseract.image_to_string(page) + "\n"
            return {"text": text.strip(), "pages": len(pages)}
        else:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return {"text": text.strip(), "pages": 1}
    except Exception as e:
        return {"error": str(e)}


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
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500,
        )
        content = response.choices[0].message.content.strip()

        # Strip markdown if present
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
        # Step 1: OCR
        ocr = extract_text(file_path)
        if "error" in ocr:
            return {
                "status": "error",
                "stage": "ocr",
                "message": ocr["error"],
            }

        text = ocr.get("text", "")
        if not text or len(text) < 20:
            return {
                "status": "error",
                "stage": "ocr",
                "message": "Document mein readable text nahi mila. Clear scan upload karo.",
            }

        # Step 2: AI Analysis
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
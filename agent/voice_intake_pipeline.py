"""
Multilingual Voice Intake Pipeline (Whisper-compatible Speech-to-Text Adapter).
Processes citizen emergency voice notes in English and Tamil (தமிழ்).
Extracts duration, sanitizes audio metadata, performs phonetic keyword mapping,
and tags vulnerability flags (e.g. stranded families, medical emergencies).
"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime, timezone


class VoiceIntakePipeline:
    """
    Ingests and processes raw citizen voice notes for emergency triage.
    Translates colloquial regional dialect cues and identifies critical urgent markers.
    """

    SUPPORTED_FORMATS = {"audio/ogg", "audio/mpeg", "audio/wav", "audio/mp4", "audio/x-m4a"}
    MAX_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB limit
    MAX_DURATION_SECONDS = 180.0       # 3 minutes

    # Colloquial glossary mappings for Tamil and Indian English
    KEYWORD_MAPPINGS = {
        "வெள்ளம்": "flood",
        "தண்ணீர்": "water",
        "மழை": "rain",
        "பாலம்": "bridge",
        "ரோடு": "road",
        "வீடு": "house",
        "சிக்கி": "trapped",
        "மருத்துவம்": "medical",
        "குழந்தை": "children",
        "முதியவர்": "elderly",
        "subway": "underpass",
        "lake": "tank_bund",
        "causeway": "bridge_culvert",
        "knee": "depth_50cm",
        "waist": "depth_90cm",
        "chest": "depth_120cm"
    }

    URGENT_CUES = [
        "trapped", "stranded", "help", "emergency", "hospital", "patient", "infant",
        "குழந்தை", "சிக்கி", "காப்பாற்றுங்கள்", "உயிருக்கு ஆபத்து", "முதியவர்"
    ]

    @classmethod
    def validate_audio_file(cls, filename: str, mime_type: str, file_size_bytes: int, duration_seconds: float) -> Dict[str, Any]:
        """
        Ensures the audio recording conforms to security and size constraints.
        """
        if mime_type not in cls.SUPPORTED_FORMATS:
            return {
                "valid": False,
                "error": f"Unsupported MIME type '{mime_type}'. Supported: {', '.join(cls.SUPPORTED_FORMATS)}"
            }

        if file_size_bytes > cls.MAX_SIZE_BYTES:
            return {
                "valid": False,
                "error": f"Audio file size exceeds 15MB limit ({file_size_bytes} bytes)"
            }

        if duration_seconds < 1.0 or duration_seconds > cls.MAX_DURATION_SECONDS:
            return {
                "valid": False,
                "error": f"Audio duration {duration_seconds}s outside acceptable window (1s - 180s)"
            }

        return {"valid": True, "error": None}

    @classmethod
    def process_transcript(
        cls,
        raw_text: str,
        detected_language: str = "en",
        audio_ref: str = "voice_001.ogg"
    ) -> Dict[str, Any]:
        """
        Analyzes speech transcript, extracts entities, and flags high-priority urgency cues.
        """
        text_lower = raw_text.lower()

        # Urgency check
        is_urgent = any(cue.lower() in text_lower for cue in cls.URGENT_CUES)

        # Depth extraction
        extracted_depth_cm = None
        match = re.search(r"(\d+)\s*(?:cm|centimeter|செமீ)", text_lower)
        if match:
            extracted_depth_cm = float(match.group(1))
        elif "waist" in text_lower or "இடுப்பு" in text_lower:
            extracted_depth_cm = 90.0
        elif "knee" in text_lower or "முழங்கால்" in text_lower:
            extracted_depth_cm = 50.0
        elif "chest" in text_lower or "மார்பு" in text_lower:
            extracted_depth_cm = 120.0

        # Terminology normalization
        matched_concepts = []
        for word, concept in cls.KEYWORD_MAPPINGS.items():
            if word in text_lower:
                matched_concepts.append(concept)

        return {
            "audio_reference": audio_ref,
            "detected_language": detected_language,
            "transcript_raw": raw_text,
            "estimated_depth_cm": extracted_depth_cm,
            "matched_concepts": list(set(matched_concepts)),
            "is_life_safety_urgent": is_urgent,
            "triage_recommendation": "IMMEDIATE_HUMAN_INSPECTION" if is_urgent else "ROUTINE_TRIAGE"
        }

"""
Quality Control and Ingestion Engine for FLOODTWIN RESPONDER.
Handles Coordinate validation, PII scrubbing, duplicate detection,
confidence scoring, and safe wording enforcement.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from geospatial.spatial_engine import haversine_distance_km
from backend.app.schemas.contracts import ReportVerificationStatus


class IngestionQCEngine:
    """
    Quality Control & Data Sanitization Pipeline.
    Assumes all incoming citizen inputs are untrusted.
    """

    # Operational District Bounding Box: Chennai Region [min_lat, max_lat, min_lon, max_lon]
    DISTRICT_BBOX = (12.80, 13.30, 79.90, 80.40)

    # Ocean / Sea Exclusion Bounding Box (Bay of Bengal deep sea)
    # Longitude > 80.32 along standard coast is open ocean
    OCEAN_EXCLUSION_LON = 80.33

    # Regex patterns for Indian phone numbers, emails, and identifiers
    PHONE_REGEX = re.compile(r"(\+91[\s-]?[6-9]\d{9}|0?[6-9]\d{9})")
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    AADHAAR_REGEX = re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b")

    # Prompt injection / Adversarial trigger keywords
    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt", re.IGNORECASE),
        re.compile(r"issue\s+(immediate\s+)?evacuation\s+order", re.IGNORECASE),
        re.compile(r"trigger\s+(the\s+)?(real\s+)?siren", re.IGNORECASE),
        re.compile(r"bypass\s+approval", re.IGNORECASE),
    ]

    def __init__(self, existing_reports: Optional[List[Dict[str, Any]]] = None):
        self.existing_reports = existing_reports or []

    def sanitize_pii(self, text: str) -> Tuple[str, List[str]]:
        """Redacts phone numbers, emails, and identity markers from text."""
        applied = []
        clean_text = text

        if self.PHONE_REGEX.search(clean_text):
            clean_text = self.PHONE_REGEX.sub("[PHONE_REDACTED]", clean_text)
            applied.append("PHONE_REDACTION")

        if self.EMAIL_REGEX.search(clean_text):
            clean_text = self.EMAIL_REGEX.sub("[EMAIL_REDACTED]", clean_text)
            applied.append("EMAIL_REDACTION")

        if self.AADHAAR_REGEX.search(clean_text):
            clean_text = self.AADHAAR_REGEX.sub("[ID_REDACTED]", clean_text)
            applied.append("ID_REDACTION")

        return clean_text, applied

    def check_adversarial(self, text: str) -> bool:
        """Detects prompt injection or unauthorized system override attempts."""
        for pat in self.ADVERSARIAL_PATTERNS:
            if pat.search(text):
                return True
        return False

    def validate_coordinates(self, lat: float, lon: float) -> Tuple[bool, str]:
        """Ensures coordinate falls strictly within operational inland district bounds."""
        min_lat, max_lat, min_lon, max_lon = self.DISTRICT_BBOX
        if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
            return False, f"Coordinate ({lat}, {lon}) is outside operational disaster jurisdiction."

        # Check ocean exclusion zone
        if lon >= self.OCEAN_EXCLUSION_LON and lat < 13.25:
            return False, f"Coordinate ({lat}, {lon}) falls into open ocean (Bay of Bengal) marine exclusion zone."

        return True, "VALID"

    def validate_timestamp(self, ts: Any) -> Tuple[bool, str]:
        """Rejects future timestamps or data older than 48 hours."""
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                return False, "Malformed timestamp format."
        now = datetime.now(timezone.utc)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        if ts > now + timedelta(minutes=5):
            return False, "Timestamp is in the future. Temporal drift rejected."
        if ts < now - timedelta(hours=48):
            return False, "Report is older than 48 hours. Stale observation rejected."
        return True, "VALID"

    def detect_duplicate(
        self,
        lat: float,
        lon: float,
        ts: Any,
        distance_threshold_m: float = 100.0,
        time_window_minutes: float = 30.0
    ) -> Optional[str]:
        """
        Detects if a report is likely a duplicate of an existing report
        within distance_threshold_m meters and time_window_minutes.
        """
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.now(timezone.utc)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        for existing in self.existing_reports:
            c = existing.get("coordinates", {})
            e_lat = c.get("latitude")
            e_lon = c.get("longitude")
            if e_lat is None or e_lon is None:
                continue

            dist_km = haversine_distance_km(lat, lon, e_lat, e_lon)
            if (dist_km * 1000.0) <= distance_threshold_m:
                e_ts_raw = existing.get("timestamp")
                if isinstance(e_ts_raw, str):
                    try:
                        e_ts = datetime.fromisoformat(e_ts_raw.replace("Z", "+00:00"))
                    except Exception:
                        continue
                else:
                    e_ts = e_ts_raw

                if e_ts:
                    if e_ts.tzinfo is None:
                        e_ts = e_ts.replace(tzinfo=timezone.utc)
                    delta_min = abs((ts - e_ts).total_seconds()) / 60.0
                    if delta_min <= time_window_minutes:
                        return existing.get("id")

        return None

    def calculate_confidence(
        self,
        text: str,
        reported_depth_cm: Optional[float],
        has_media: bool = False,
        source: str = "CITIZEN_APP"
    ) -> float:
        """Calculates credibility score (0.0 to 1.0)."""
        score = 0.50
        if source == "FIELD_INSPECTOR":
            score += 0.35
        elif source == "EMERGENCY_HOTLINE":
            score += 0.25
        elif source == "CITIZEN_APP":
            score += 0.15

        if reported_depth_cm is not None and 5.0 <= reported_depth_cm <= 200.0:
            score += 0.15

        if has_media:
            score += 0.10

        # Penalize ultra-short ambiguous text
        if len(text.strip().split()) < 4:
            score -= 0.20

        return round(min(1.0, max(0.10, score)), 2)

    def process_report(
        self,
        report_id: str,
        raw_text: str,
        lat: float,
        lon: float,
        timestamp: datetime,
        source: str = "CITIZEN_APP",
        reported_depth_cm: Optional[float] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes full QC workflow on incoming report."""
        # 1. Adversarial Injection Check
        if self.check_adversarial(raw_text):
            return {
                "accepted": False,
                "status": ReportVerificationStatus.ADVERSARIAL_SUPPRESSED.value,
                "reason": "Security Alert: Adversarial prompt injection pattern detected and suppressed.",
                "confidence": 0.0
            }

        # 2. Coordinates validation
        coord_valid, coord_msg = self.validate_coordinates(lat, lon)
        if not coord_valid:
            return {
                "accepted": False,
                "status": ReportVerificationStatus.REJECTED_IMPOSSIBLE.value,
                "reason": coord_msg,
                "confidence": 0.0
            }

        # 3. Timestamp validation
        time_valid, time_msg = self.validate_timestamp(timestamp)
        if not time_valid:
            return {
                "accepted": False,
                "status": ReportVerificationStatus.REJECTED_IMPOSSIBLE.value,
                "reason": time_msg,
                "confidence": 0.0
            }

        # 4. PII Redaction
        clean_text, applied_sanitizations = self.sanitize_pii(raw_text)

        # 5. Duplicate Detection
        dup_parent_id = self.detect_duplicate(lat, lon, timestamp)
        if dup_parent_id:
            status = ReportVerificationStatus.LIKELY_DUPLICATE.value
        else:
            status = ReportVerificationStatus.POSSIBLE_WATERLOGGING.value

        # 6. Confidence Scoring
        confidence = self.calculate_confidence(
            text=clean_text,
            reported_depth_cm=reported_depth_cm,
            has_media=bool(image_url),
            source=source
        )

        return {
            "accepted": True,
            "id": report_id,
            "status": status,
            "duplicate_of": dup_parent_id,
            "sanitized_description": clean_text,
            "sanitizations_applied": applied_sanitizations,
            "confidence": confidence,
            "verification_wording": "possible waterlogging" if not dup_parent_id else "likely duplicate",
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def mock_transcribe_audio(audio_filename: str) -> Dict[str, Any]:
        """Whisper-compatible adapter returning speech-to-text transcript and confidence."""
        return {
            "transcript": "Ground floor house flooded water level is around 2 feet near subway road",
            "detected_language": "en",
            "confidence": 0.93,
            "adapter": "Whisper-STT-v3-Adapter"
        }

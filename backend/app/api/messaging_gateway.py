"""
Two-Way Citizen Messaging Gateway (WhatsApp, IVR, SMS Adapter).
Ingests inbound citizen flood reports, parses geotagged coordinates,
masks citizen phone numbers/PII, verifies webhook HMAC signatures,
and generates bilingual (English / Tamil) conversational receipts.
"""

from typing import Dict, Any, Optional
import hmac
import hashlib
import re
from datetime import datetime, timezone


class MessagingGateway:
    """
    Parses incoming webhook messages from communication gateways (Meta WhatsApp Cloud API, Twilio, Gupshup).
    Ensures PII masking and cryptographic HMAC signature validation.
    """

    WEBHOOK_SECRET = "floodtwin_demo_webhook_secret_2026"

    @classmethod
    def verify_signature(cls, raw_body: bytes, signature_header: str, secret: Optional[str] = None) -> bool:
        """
        Validates HMAC-SHA256 signature (e.g., 'sha256=abcdef...').
        """
        key = (secret or cls.WEBHOOK_SECRET).encode("utf-8")
        computed = hmac.new(key, raw_body, hashlib.sha256).hexdigest()

        # Support 'sha256=' prefix if present
        sig = signature_header.split("=")[-1] if "=" in signature_header else signature_header
        return hmac.compare_digest(computed, sig)

    @staticmethod
    def mask_phone_number(phone: str) -> str:
        """
        Redacts intermediate digits of telephone number for privacy compliance.
        Example: '+919876543210' -> '+91 98****3210'
        """
        clean = re.sub(r"[^\d+]", "", phone)
        if len(clean) < 8:
            return "****"
        return f"{clean[:5]}****{clean[-4:]}"

    @classmethod
    def parse_whatsapp_webhook(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts structured flood report details from WhatsApp message payload.
        Handles text descriptions, live location coordinates, and media attachments.
        """
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [{}])

        if not messages:
            raise ValueError("No message body located in webhook payload.")

        msg = messages[0]
        from_phone = msg.get("from", "UNKNOWN")
        msg_type = msg.get("type", "text")
        masked_phone = cls.mask_phone_number(from_phone)

        extracted = {
            "source": "whatsapp_citizen",
            "sender_masked": masked_phone,
            "message_id": msg.get("id"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "has_location": False,
            "latitude": None,
            "longitude": None,
            "text": "",
            "estimated_depth_cm": None,
            "language": "en"
        }

        if msg_type == "text":
            body = msg.get("text", {}).get("body", "")
            extracted["text"] = body
            # Simple heuristic for depth extraction (e.g., 'water level 40cm' or 'knee deep')
            match = re.search(r"(\d+)\s*(?:cm|centimeter|செமீ)", body, re.IGNORECASE)
            if match:
                extracted["estimated_depth_cm"] = float(match.group(1))
            elif "knee" in body.lower() or "முழங்கால்" in body:
                extracted["estimated_depth_cm"] = 50.0
            elif "waist" in body.lower() or "இடுப்பு" in body:
                extracted["estimated_depth_cm"] = 90.0

            # Language check
            if any("\u0b80" <= char <= "\u0bff" for char in body):
                extracted["language"] = "ta"

        elif msg_type == "location":
            loc = msg.get("location", {})
            extracted["has_location"] = True
            extracted["latitude"] = loc.get("latitude")
            extracted["longitude"] = loc.get("longitude")
            extracted["text"] = loc.get("name") or loc.get("address") or "Geotagged citizen pin"

        return extracted

    @classmethod
    def generate_acknowledgement(cls, language: str = "en", tracking_id: str = "FT-001") -> str:
        """
        Returns polite, comforting acknowledgement with safety guidance.
        """
        if language == "ta":
            return (
                f"நன்றி. உங்கள் வெள்ள அறிக்கை பதிவு செய்யப்பட்டது (எண்: {tracking_id}). "
                "எங்கள் பேரிடர் கட்டுப்பாட்டு குழுவினர் இதனை சரிபார்க்கின்றனர். "
                "நீர்வரத்து அதிகம் உள்ள பாலங்கள் மற்றும் மின் கம்பங்களை தொடாதீர்கள். பாதுகாப்பாக இருங்கள்."
            )
        return (
            f"Thank you. Your flood observation has been logged (Ref: {tracking_id}). "
            "Our municipal response team is verifying this report. "
            "Please avoid submerged causeways and stay clear of electrical poles. Stay safe."
        )

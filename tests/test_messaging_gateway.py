import pytest
import json
import hmac
import hashlib
from backend.app.api.messaging_gateway import MessagingGateway


def test_hmac_signature_verification():
    secret = "secret_key_xyz"
    body = b'{"status": "ok"}'
    valid_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    assert MessagingGateway.verify_signature(body, f"sha256={valid_sig}", secret=secret) is True
    assert MessagingGateway.verify_signature(body, "sha256=invalid_hex_string", secret=secret) is False


def test_phone_number_masking():
    masked = MessagingGateway.mask_phone_number("+919876543210")
    assert "98****3210" in masked
    assert "7654" not in masked


def test_whatsapp_text_message_depth_extraction():
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "+919876543210",
                        "id": "wamid.123",
                        "type": "text",
                        "text": {"body": "Water depth is around 65 cm near Singanallur lake bus stop"}
                    }]
                }
            }]
        }]
    }

    report = MessagingGateway.parse_whatsapp_webhook(payload)
    assert report["estimated_depth_cm"] == 65.0
    assert "98****3210" in report["sender_masked"]
    assert report["language"] == "en"

    ack = MessagingGateway.generate_acknowledgement("en", "FT-999")
    assert "logged (Ref: FT-999)" in ack


def test_whatsapp_tamil_text_extraction():
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "+919444455555",
                        "id": "wamid.456",
                        "type": "text",
                        "text": {"body": "இங்கே முழங்கால் அளவு தண்ணீர் தேங்கியுள்ளது"}
                    }]
                }
            }]
        }]
    }

    report = MessagingGateway.parse_whatsapp_webhook(payload)
    assert report["language"] == "ta"
    assert report["estimated_depth_cm"] == 50.0  # knee-deep heuristic

    ack = MessagingGateway.generate_acknowledgement("ta", "FT-TAMIL-01")
    assert "நன்றி" in ack

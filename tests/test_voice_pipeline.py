import pytest
from agent.voice_intake_pipeline import VoiceIntakePipeline


def test_audio_file_validation_constraints():
    # Valid ogg voice note
    v1 = VoiceIntakePipeline.validate_audio_file(
        filename="citizen_audio.ogg",
        mime_type="audio/ogg",
        file_size_bytes=1024 * 500,  # 500 KB
        duration_seconds=25.0
    )
    assert v1["valid"] is True

    # Invalid MIME type
    v2 = VoiceIntakePipeline.validate_audio_file(
        filename="malicious.exe",
        mime_type="application/x-msdownload",
        file_size_bytes=1000,
        duration_seconds=10.0
    )
    assert v2["valid"] is False
    assert "Unsupported MIME" in v2["error"]

    # Duration too long (> 180s)
    v3 = VoiceIntakePipeline.validate_audio_file(
        filename="podcast.mp3",
        mime_type="audio/mpeg",
        file_size_bytes=1024 * 1024,
        duration_seconds=250.0
    )
    assert v3["valid"] is False
    assert "duration" in v3["error"].lower()


def test_transcript_processing_urgent_tamil():
    # Tamil transcript mentioning trapped elderly people and waist-deep water
    raw_ta = "எங்கள் தெருவில் வெள்ளம் இடுப்பு அளவு உள்ளது. முதியவர் மற்றும் குழந்தை சிக்கி உள்ளனர் உதவி தேவை."
    res = VoiceIntakePipeline.process_transcript(raw_ta, detected_language="ta")

    assert res["is_life_safety_urgent"] is True
    assert res["triage_recommendation"] == "IMMEDIATE_HUMAN_INSPECTION"
    assert res["estimated_depth_cm"] == 90.0  # waist level
    assert "elderly" in res["matched_concepts"]
    assert "flood" in res["matched_concepts"]


def test_transcript_processing_english_routine():
    raw_en = "Mild waterlogging near the railway subway, water depth is around 25cm on the road."
    res = VoiceIntakePipeline.process_transcript(raw_en, detected_language="en")

    assert res["is_life_safety_urgent"] is False
    assert res["triage_recommendation"] == "ROUTINE_TRIAGE"
    assert res["estimated_depth_cm"] == 25.0
    assert "underpass" in res["matched_concepts"]

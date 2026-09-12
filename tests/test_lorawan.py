import pytest
from backend.app.services.lorawan_decoder import LoRaWANDecoder


def test_lorawan_encode_decode_roundtrip():
    # Ultrasonic sensor (0x01), 2450 mm (2.45m), 3.7V (37), 42.5mm rain (425), flags=0
    payload = LoRaWANDecoder.encode_test_payload(
        sensor_type_code=0x01,
        water_level_mm=2450,
        battery_tenths_v=37,
        rainfall_tenths_mm=425,
        flags=0
    )
    assert len(payload) == 8

    res = LoRaWANDecoder.decode_payload(payload, sensor_id="TEST_01")
    assert res["sensor_id"] == "TEST_01"
    assert res["sensor_type"] == "ULTRASONIC_STAGE"
    assert res["water_level_m"] == 2.45
    assert res["battery_volts"] == 3.70
    assert res["rainfall_last_hour_mm"] == 42.5
    assert res["status"] == "warning"  # >= 1.5m
    assert res["crc_verified"] is True
    assert res["hardware_flags"]["low_battery"] is False


def test_lorawan_crc_rejection():
    # Construct payload and corrupt CRC byte
    valid_payload = LoRaWANDecoder.encode_test_payload(
        sensor_type_code=0x02,
        water_level_mm=1000,
        battery_tenths_v=33,
        rainfall_tenths_mm=0,
        flags=0x01  # low battery flag
    )
    corrupted_payload = valid_payload[:7] + bytes([(valid_payload[7] ^ 0xFF)])

    with pytest.raises(ValueError, match="CRC-8 verification failed"):
        LoRaWANDecoder.decode_payload(corrupted_payload)


def test_lorawan_hardware_fault_flag():
    # Sensor fault flag bit 3 (0x08)
    payload = LoRaWANDecoder.encode_test_payload(
        sensor_type_code=0x01,
        water_level_mm=500,
        battery_tenths_v=36,
        rainfall_tenths_mm=10,
        flags=0x08
    )
    res = LoRaWANDecoder.decode_payload(payload)
    assert res["status"] == "fault"
    assert res["hardware_flags"]["sensor_fault"] is True

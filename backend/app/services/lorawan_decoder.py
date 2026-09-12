"""
LoRaWAN Binary Telemetry Decoder for FloodTwin IoT Sensors.
Decodes compact binary payloads transmitted by ultrasonic gauges,
hydrostatic pressure transducers, and tipping bucket rain sensors.
Includes CRC8 data integrity verification and hardware health status flags.
"""

from typing import Dict, Any, Optional
import struct


class LoRaWANDecoder:
    """
    Decodes binary LoRaWAN uplink payloads (Hex or Base64).
    Packet Structure (8 bytes):
      [0]   : Header / Sensor Type (0x01: Ultrasonic, 0x02: Hydrostatic, 0x03: Tipping Bucket)
      [1:3] : Water Stage Level (uint16 big-endian, mm)
      [3]   : Battery Voltage (uint8, in 0.1V, e.g. 37 = 3.7V)
      [4:6] : Rainfall Accumulation (uint16 big-endian, in 0.1mm)
      [6]   : Status Flags (Bit 0: Low Battery, Bit 1: Tamper, Bit 2: Submerged, Bit 3: Sensor Fault)
      [7]   : CRC-8 Checksum (Dallas/Maxim polynomial 0x31 or 0x07)
    """

    POLYNOMIAL = 0x07

    @classmethod
    def calculate_crc8(cls, data: bytes) -> int:
        """Calculates standard CRC-8 with polynomial 0x07 and initial value 0x00."""
        crc = 0x00
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ cls.POLYNOMIAL) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    @classmethod
    def decode_payload(
        cls,
        payload_bytes: bytes,
        sensor_id: str = "LORA_SENSOR_01",
        sensor_name: str = "Noyyal Bridge IoT Gauge",
        lat: float = 11.00,
        lon: float = 76.96
    ) -> Dict[str, Any]:
        """
        Validates CRC and extracts engineering metrics from binary telemetry.
        """
        if len(payload_bytes) != 8:
            raise ValueError(f"Invalid LoRaWAN payload length: expected 8 bytes, received {len(payload_bytes)}")

        data_part = payload_bytes[:7]
        expected_crc = payload_bytes[7]
        computed_crc = cls.calculate_crc8(data_part)

        if computed_crc != expected_crc:
            raise ValueError(f"CRC-8 verification failed: computed 0x{computed_crc:02X} != packet 0x{expected_crc:02X}")

        sensor_type_code, raw_water_mm, raw_batt, raw_rain, flags = struct.unpack(">BHBHB", payload_bytes[:7])

        sensor_types = {
            0x01: "ULTRASONIC_STAGE",
            0x02: "HYDROSTATIC_PRESSURE",
            0x03: "TIPPING_BUCKET_RAIN"
        }
        sensor_type = sensor_types.get(sensor_type_code, "UNKNOWN")

        water_level_m = round(raw_water_mm / 1000.0, 3)
        battery_volts = round(raw_batt / 10.0, 2)
        rainfall_mm = round(raw_rain / 10.0, 1)

        low_battery = bool(flags & 0x01)
        tamper_alert = bool(flags & 0x02)
        submerged_alert = bool(flags & 0x04)
        sensor_fault = bool(flags & 0x08)

        # Operational status assessment
        if sensor_fault:
            status = "fault"
        elif submerged_alert:
            status = "critical"
        elif water_level_m >= 3.0:
            status = "alert"
        elif water_level_m >= 1.5:
            status = "warning"
        else:
            status = "nominal"

        return {
            "sensor_id": sensor_id,
            "sensor_name": sensor_name,
            "sensor_type": sensor_type,
            "latitude": lat,
            "longitude": lon,
            "water_level_m": water_level_m,
            "rainfall_last_hour_mm": rainfall_mm,
            "battery_volts": battery_volts,
            "status": status,
            "hardware_flags": {
                "low_battery": low_battery,
                "tamper": tamper_alert,
                "submerged": submerged_alert,
                "sensor_fault": sensor_fault
            },
            "crc_verified": True
        }

    @classmethod
    def encode_test_payload(
        cls,
        sensor_type_code: int,
        water_level_mm: int,
        battery_tenths_v: int,
        rainfall_tenths_mm: int,
        flags: int
    ) -> bytes:
        """Helper to construct and sign an 8-byte LoRaWAN test frame."""
        data_part = struct.pack(">BHBHB", sensor_type_code, water_level_mm, battery_tenths_v, rainfall_tenths_mm, flags)
        crc = cls.calculate_crc8(data_part)
        return data_part + bytes([crc])

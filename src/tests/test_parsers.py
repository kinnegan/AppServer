import pytest
from unittest.mock import MagicMock
from src.modules.parsers import (
    decode_base64, decode_cobs, decode_command,
    check_device, process_measurements, parse_measurement, parse_value
    )
from cobs import cobs
from datetime import datetime


def test_decode_base64_valid():
    data = "SGVsbG8gd29ybGQ="
    decoded = decode_base64(data)
    assert decoded == b"Hello world"

def test_decode_base64_invalid():
    data = "invalid_base64"
    with pytest.raises(ValueError, match="Ошибка декодирования base64"):
        decode_base64(data)

def test_decode_cobs_valid():
    data = b"\x01\x02\x03"
    encoded = cobs.encode(data)
    decoded = decode_cobs(encoded)
    assert decoded == data

def test_decode_cobs_invalid():
    data = b"\x00\x00"
    with pytest.raises(ValueError, match="Ошибка COBS-декодирования"):
        decode_cobs(data)

def test_decode_command_valid():
    data = b"\x01\x02\x00\x01\x00\xff\xfftestdata"  # len = 2 (0x02 0x00)
    command = decode_command(data)
    assert command["code"] == 1
    assert command["len"] == 2
    assert command["devType"] == "Цельсиум"
    assert command["crc"] == 65535
    assert command["commandData"] == b"testdata"

def test_decode_command_invalid():
    data = b""
    with pytest.raises(ValueError, match="Нулевая длина команды"):
        decode_command(data)

def test_process_measurements():
    command = {
        "commandData": b"\x00" + b"\x01" * 20 + b"\x02" * 20,
        "code": 1,
    }
    measurements = process_measurements(command)
    assert len(measurements) == 2

def test_parse_measurement_valid():
    data = b"\x00" + b"\x10\x00\x00\x00" + b"\x01" * 16
    measurement = parse_measurement(data, 0, 1)
    assert measurement["id"] == 1
    assert measurement["temperature"] == 257
    assert measurement["humidity"] == 2.6
    assert measurement["lux"] == 257
    assert measurement["noise"] == 257
    assert measurement["co2"] == 257
    assert measurement["voltage"] == 0.26
    assert measurement["date"] == datetime.fromtimestamp(16).strftime("%d.%m.%Y")
    assert measurement["time"] == datetime.fromtimestamp(16).strftime("%H:%M:%S")

def test_parse_measurement_invalid():
    data = b"\x00" + b"\x10\x00\x00\x00" + b"\xff\xff" * 8
    measurement = parse_measurement(data, 0, 1)
    assert measurement is None

def test_parse_value():
    data = b"\x01\x02"
    value = parse_value(data)
    assert value == 513

def test_check_device(mocker):
    mocker.patch("src.modules.parsers.collection.find_one", return_value=None)
    mocker.patch("src.modules.parsers.collection.insert_one")
    assert check_device("123", "test", "app_id", "config_id") == "add"

    mocker.patch("src.modules.parsers.collection.find_one", return_value={"external_id": "123"})
    mocker.patch("src.modules.parsers.collection.update_one")
    assert check_device("123", "test", "app_id", "config_id") == "update"

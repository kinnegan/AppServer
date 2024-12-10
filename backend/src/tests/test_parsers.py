import pytest
from unittest.mock import MagicMock
from src.modules.parsers import (
    decode_base64, decode_cobs, decode_command,
    check_device, process_measurements, parse_measurement, parse_value
    )
from cobs import cobs
from datetime import datetime


@pytest.fixture
def mock_collection():
    """мок-объект коллекции MongoDB."""
    return MagicMock()


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


def test_process_measurements(mock_collection):
    command = {
        "commandData": b"\x00" + b"\x01" * 20 + b"\x02" * 20,
        "code": 1,
    }
    measurements = process_measurements(command, "test@exterma.id", collection=mock_collection)

    assert len(measurements) == 2

    assert mock_collection.insert_one.call_count == 2


def test_parse_measurement_valid():
    data = b"\x00" + b"\x10\x00\x00\x00" + b"\x01" * 16
    measurement = parse_measurement(data, 0, 1, "test@exterma.id")
    assert measurement["id"] == 1
    assert measurement["temperature"] == 2.57
    assert measurement["humidity"] == 2.57
    assert measurement["lux"] == 257
    assert measurement["noise"] == 257
    assert measurement["co2"] == 257
    assert measurement["voltage"] == 0.26
    assert measurement["date"] == '01-01-1970'
    assert measurement["time"] == '00:00:16'


def test_parse_value():
    data = b"\x01\x02"
    value = parse_value(data)
    assert value == 258


def test_check_device(mock_collection):
    fixed_now = datetime.now()

    mock_collection.find_one.return_value = None
    result = check_device("test@exterma.id", "test", "app_id", "config_id", collection=mock_collection)
    assert result == "add"
    insert_args = mock_collection.insert_one.call_args[0][0]

    assert insert_args["external_id"] == "test@exterma.id"
    assert insert_args["dev_type"] == "test"
    assert insert_args["application_id"] == "app_id"
    assert insert_args["config_id"] == "config_id"
    assert abs((insert_args["added"] - fixed_now).total_seconds()) < 1  # Допустимое отклонение в 1 секунду (для использования в CI)

    mock_collection.find_one.return_value = {"external_id": "test@exterma.id"}
    mock_collection.reset_mock()

    result = check_device("test@exterma.id", "test", "app_id", "config_id", collection=mock_collection)

    assert result == "update"
    update_args = mock_collection.update_one.call_args[0][1]

    assert abs((update_args["$set"]["lastHeard"] - fixed_now).total_seconds()) < 1  # Допустимое отклонение в 1 секунду (для использования в CI)

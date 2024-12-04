import pytest
from unittest.mock import MagicMock
from src.modules.parsers import decode_base64, decode_cobs, decode_command, check_device, process_measurements


def test_decode_base64():
    assert decode_base64("dGVzdA==") == b"test"
    with pytest.raises(ValueError):
        decode_base64("invalid_base64")

def test_decode_cobs():
    from cobs import cobs
    data = b"test"
    assert decode_cobs(cobs.encode(data)) == data
    with pytest.raises(ValueError):
        decode_cobs(b"invalid_cobs")

def test_decode_command():
    data = bytes([1, 0, 0, 3, 0, 0, 0, 0])
    command = decode_command(data)
    assert command["code"] == 1
    assert command["devType"] == "Цельсиум-2 (CO2)"
    with pytest.raises(ValueError):
        decode_command(b"")

def test_check_device(mocker):
    mocker.patch("src.modules.parsers.collection.find_one", return_value=None)
    mocker.patch("src.modules.parsers.collection.insert_one")
    assert check_device("123", "test", "app_id", "config_id") == "add"

    mocker.patch("src.modules.parsers.collection.find_one", return_value={"external_id": "123"})
    mocker.patch("src.modules.parsers.collection.update_one")
    assert check_device("123", "test", "app_id", "config_id") == "update"

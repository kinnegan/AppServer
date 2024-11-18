import pytest
from service import decode_base64, decode_cobs, decode_command, process_measurements

def test_decode_base64():
    assert decode_base64("dGVzdA==") == b"test"

def test_decode_cobs():
    assert decode_cobs(b'\x03\x01\x02') == b'\x01\x02'

def test_decode_command():
    data = b'\x01\x10\x00\x01\x00\x00\x00\x00'
    command = decode_command(data)
    assert command['code'] == 1
    assert command['devType'] == "Цельсиум"

def test_process_measurements():
    command = {
        'code': 1,
        'commandData': b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    }
    measurements = process_measurements(command)
    assert len(measurements) == 1

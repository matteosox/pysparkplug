"""Module defining the DataType enum"""

import datetime
import enum
from typing import Union, List, Any, Callable
import struct

from pysparkplug._types import MetricValue

__all__ = ["DataType"]


class DataType(enum.IntEnum):
    """Enumeration of Sparkplug B datatypes"""

    UNKNOWN = 0
    INT8 = 1
    INT16 = 2
    INT32 = 3
    INT64 = 4
    UINT8 = 5
    UINT16 = 6
    UINT32 = 7
    UINT64 = 8
    FLOAT = 9
    DOUBLE = 10
    BOOLEAN = 11
    STRING = 12
    DATETIME = 13
    TEXT = 14
    UUID = 15
    DATASET = 16
    BYTES = 17
    FILE = 18
    TEMPLATE = 19
    PROPERTYSET = 20
    PROPERTYSETLIST = 21
    
    # Array Types - values starting at 22 per Sparkplug B spec
    INT8_ARRAY = 22
    INT16_ARRAY = 23
    INT32_ARRAY = 24
    INT64_ARRAY = 25
    UINT8_ARRAY = 26
    UINT16_ARRAY = 27
    UINT32_ARRAY = 28
    UINT64_ARRAY = 29
    FLOAT_ARRAY = 30
    DOUBLE_ARRAY = 31
    BOOLEAN_ARRAY = 32
    STRING_ARRAY = 33
    DATETIME_ARRAY = 34

    @property
    def field(self) -> str:
        """The Protobuf field the data is encoded in"""
        try:
            return _fields[self]
        except KeyError as exc:
            raise ValueError(f"{self} has no field name") from exc

    def encode(self, value: MetricValue) -> Union[int, float, bool, str, bytes]:
        """Encode a value into the form it should take in a Sparkplug B Protobuf object"""
        try:
            encoder = _encoders[self]
        except KeyError as exc:
            raise ValueError(f"{self} cannot be encoded") from exc
        return encoder(value)

    def decode(self, value: Union[int, float, bool, str, bytes]) -> MetricValue:
        """Decode a value from the form it takes in a Sparkplug B Protobuf object"""
        try:
            decoder = _decoders[self]
        except KeyError as exc:
            raise ValueError(f"{self} cannot be decoded") from exc
        return decoder(value)


_fields = {
    DataType.UINT8: "int_value",
    DataType.UINT16: "int_value",
    DataType.UINT32: "int_value",
    DataType.UINT64: "long_value",
    DataType.INT8: "int_value",
    DataType.INT16: "int_value",
    DataType.INT32: "int_value",
    DataType.INT64: "long_value",
    DataType.FLOAT: "float_value",
    DataType.DOUBLE: "double_value",
    DataType.BOOLEAN: "boolean_value",
    DataType.STRING: "string_value",
    DataType.DATETIME: "long_value",
    DataType.TEXT: "string_value",
    DataType.UUID: "string_value",
    DataType.BYTES: "bytes_value",
    DataType.FILE: "bytes_value",
    DataType.INT8_ARRAY: "bytes_value",
    DataType.INT16_ARRAY: "bytes_value",
    DataType.INT32_ARRAY: "bytes_value",
    DataType.INT64_ARRAY: "bytes_value",
    DataType.UINT8_ARRAY: "bytes_value",
    DataType.UINT16_ARRAY: "bytes_value",
    DataType.UINT32_ARRAY: "bytes_value",
    DataType.UINT64_ARRAY: "bytes_value",
    DataType.FLOAT_ARRAY: "bytes_value",
    DataType.DOUBLE_ARRAY: "bytes_value",
    DataType.BOOLEAN_ARRAY: "bytes_value",
    DataType.STRING_ARRAY: "bytes_value",
    DataType.DATETIME_ARRAY: "bytes_value",
}

def _encode_array_to_bytes(values: List[Any], format_char: str) -> bytes:
    """Convert array to bytes using specified format
    
    Args:
        values: List of values to encode
        format_char: Format character for struct.pack:
            'b' = int8, 'B' = uint8
            'h' = int16, 'H' = uint16
            'i' = int32, 'I' = uint32
            'q' = int64, 'Q' = uint64
            'f' = float
            'd' = double
    """
    format_str = f"!{len(values)}{format_char}"  # '!' for network byte order
    try:
        return struct.pack(format_str, *values)
    except struct.error as e:
        raise ValueError(f"Failed to encode array values {values} with format {format_char}: {e}")

_encoders = {
    # Scalar encoders
    DataType.INT8: lambda val: val,
    DataType.INT16: lambda val: val,
    DataType.INT32: lambda val: val,
    DataType.INT64: lambda val: val,
    DataType.UINT8: lambda val: val,
    DataType.UINT16: lambda val: val,
    DataType.UINT32: lambda val: val,
    DataType.UINT64: lambda val: val,
    DataType.FLOAT: lambda val: val,
    DataType.DOUBLE: lambda val: val,
    DataType.BOOLEAN: lambda val: val,
    DataType.STRING: lambda val: val,
    DataType.DATETIME: lambda val: int(val.timestamp() * 1000),
    DataType.TEXT: lambda val: val,
    DataType.UUID: lambda val: val,
    DataType.BYTES: lambda val: val,
    DataType.FILE: lambda val: val,
    
    # Array encoders
    DataType.INT8_ARRAY: lambda val: _encode_array_to_bytes(val, 'b'),
    DataType.INT16_ARRAY: lambda val: _encode_array_to_bytes(val, 'h'),
    DataType.INT32_ARRAY: lambda val: _encode_array_to_bytes(val, 'i'),
    DataType.INT64_ARRAY: lambda val: _encode_array_to_bytes(val, 'q'),
    DataType.UINT8_ARRAY: lambda val: _encode_array_to_bytes(val, 'B'),
    DataType.UINT16_ARRAY: lambda val: _encode_array_to_bytes(val, 'H'),
    DataType.UINT32_ARRAY: lambda val: _encode_array_to_bytes(val, 'I'),
    DataType.UINT64_ARRAY: lambda val: _encode_array_to_bytes(val, 'Q'),
    DataType.FLOAT_ARRAY: lambda val: _encode_array_to_bytes(val, 'f'),
    DataType.DOUBLE_ARRAY: lambda val: _encode_array_to_bytes(val, 'd'),
    DataType.BOOLEAN_ARRAY: lambda val: bytes([1 if x else 0 for x in val]),
    DataType.STRING_ARRAY: lambda val: b'\0'.join(s.encode('utf-8') for s in val) + b'\0',
    DataType.DATETIME_ARRAY: lambda val: _encode_array_to_bytes(
        [int(v.timestamp() * 1000) for v in val], 'q'
    ),
}

def _validate_int_array(values: List[Any], bits: int, signed: bool = True) -> List[int]:
    """Validates each integer value in an array fits within specified bit range
    
    Args:
        values: List of integer values to validate
        bits: Number of bits each integer should fit in
        signed: Whether the integers are signed or unsigned
    
    Returns:
        The validated list of integers
    
    Raises:
        ValueError: If any value is outside the valid range for the specified bits
    """
    decoder = _int_decoder(bits, signed)
    return [decoder(v) for v in values]

def _decode_bytes_to_array(data: bytes, format_char: str) -> List[Any]:
    """Convert bytes back to array using specified format
    
    Args:
        data: Bytes to decode
        format_char: Format character for struct.unpack:
            'b' = int8, 'B' = uint8
            'h' = int16, 'H' = uint16
            'i' = int32, 'I' = uint32
            'q' = int64, 'Q' = uint64
            'f' = float
            'd' = double
    """
    size = struct.calcsize(format_char)
    count = len(data) // size
    format_str = f"!{count}{format_char}"  # '!' for network byte order
    try:
        return list(struct.unpack(format_str, data))
    except struct.error as e:
        raise ValueError(f"Failed to decode bytes {data} with format {format_char}: {e}")

_decoders = {
    DataType.UINT8: lambda val: _uint_coder(val, 8),
    DataType.UINT16: lambda val: _uint_coder(val, 16),
    DataType.UINT32: lambda val: _uint_coder(val, 32),
    DataType.UINT64: lambda val: _uint_coder(val, 64),
    DataType.INT8: lambda val: _int_decoder(val, 8),
    DataType.INT16: lambda val: _int_decoder(val, 16),
    DataType.INT32: lambda val: _int_decoder(val, 32),
    DataType.INT64: lambda val: _int_decoder(val, 64),
    DataType.FLOAT: lambda val: val,
    DataType.DOUBLE: lambda val: val,
    DataType.BOOLEAN: lambda val: val,
    DataType.STRING: lambda val: val,
    DataType.DATETIME: lambda val: datetime.datetime.fromtimestamp(
        val * 1e-3, tz=datetime.timezone.utc
    ),
    DataType.TEXT: lambda val: val,
    DataType.UUID: lambda val: val,
    DataType.BYTES: lambda val: val,
    DataType.FILE: lambda val: val,
    
    # Array decoders with validation
    DataType.INT8_ARRAY: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'b'), 8),
    DataType.INT16_ARRAY: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'h'), 16),
    DataType.INT32_ARRAY: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'i'), 32),
    DataType.INT64_ARRAY: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'q'), 64),
    DataType.UINT8_ARRAY: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'B'), 8, signed=False),
    DataType.UINT16_ARRAY: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'H'), 16, signed=False),
    DataType.UINT32_ARRAY: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'I'), 32, signed=False),
    DataType.UINT64_ARRAY: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'Q'), 64, signed=False),
    DataType.FLOAT_ARRAY: lambda val: _decode_bytes_to_array(val, 'f'),
    DataType.DOUBLE_ARRAY: lambda val: _decode_bytes_to_array(val, 'd'),
    DataType.BOOLEAN_ARRAY: lambda val: [bool(b) for b in val],
    DataType.STRING_ARRAY: lambda val: [s.decode('utf-8') for s in val.split(b'\0') if s],
    DataType.DATETIME_ARRAY: lambda val: [
        datetime.datetime.fromtimestamp(v/1000, datetime.timezone.utc) 
        for v in _decode_bytes_to_array(val, 'q')
    ],
}


def _uint_coder(value: int, bits: int) -> int:
    if not 0 <= value < 2**bits:
        raise OverflowError(f"UInt{bits} overflow with value {value}")
    return value


def _int_encoder(value: int, bits: int) -> int:
    max_val: int = 2 ** (bits - 1)
    if not -max_val <= value < max_val:
        raise OverflowError(f"Int{bits} overflow with value {value}")
    return value + (max_val * 2 if value < 0 else 0)


def _int_decoder(bits: int, signed: bool = True) -> Callable[[int], int]:
    """Returns a function that validates and decodes an integer value"""
    if signed:
        min_val = -(2 ** (bits - 1))
        max_val = (2 ** (bits - 1)) - 1
    else:
        min_val = 0
        max_val = (2 ** bits) - 1

    def decoder(value: int) -> int:
        if not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value)}")
        if not min_val <= value <= max_val:
            raise ValueError(
                f"Value {value} outside valid range [{min_val}, {max_val}]"
            )
        return value

    return decoder

"""Module defining the DataType enum"""

import datetime
import enum
import struct
from typing import Any, List, Union

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
        raise ValueError(
            f"Failed to encode array values {values} with format {format_char}: {e}"
        )


def validate_integer_range(value: int, bits: int, signed: bool = False) -> int:
    """Validate integer values are within their bit range and return the value if valid.

    Args:
        value: Integer value to validate
        bits: Number of bits for the integer type
        signed: If True, treat as signed int, otherwise as unsigned int

    Returns:
        The validated integer value

    Raises:
        TypeError: If value is not an integer
        OverflowError: If value is outside valid range for the specified bits
    """
    if not isinstance(value, int):
        raise TypeError(f"Expected int, got {type(value)}")

    if signed:
        max_val = 2 ** (bits - 1)
        if not -max_val <= value < max_val:
            raise OverflowError(f"Int{bits} overflow with value {value}")
    elif not 0 <= value < 2**bits:
        raise OverflowError(f"UInt{bits} overflow with value {value}")
    return value


_encoders = {
    # Unsigned integers (default)
    DataType.UINT8: lambda val: validate_integer_range(val, 8),
    DataType.UINT16: lambda val: validate_integer_range(val, 16),
    DataType.UINT32: lambda val: validate_integer_range(val, 32),
    DataType.UINT64: lambda val: validate_integer_range(val, 64),
    # Signed integers (explicit signed=True)
    DataType.INT8: lambda val: validate_integer_range(val, 8, signed=True),
    DataType.INT16: lambda val: validate_integer_range(val, 16, signed=True),
    DataType.INT32: lambda val: validate_integer_range(val, 32, signed=True),
    DataType.INT64: lambda val: validate_integer_range(val, 64, signed=True),
    # Array encoders - validate before encoding
    DataType.INT8_ARRAY: lambda val: _encode_array_to_bytes(
        [validate_integer_range(v, 8, signed=True) for v in val], "b"
    ),
    DataType.INT16_ARRAY: lambda val: _encode_array_to_bytes(
        [validate_integer_range(v, 16, signed=True) for v in val], "h"
    ),
    DataType.INT32_ARRAY: lambda val: _encode_array_to_bytes(
        [validate_integer_range(v, 32, signed=True) for v in val], "i"
    ),
    DataType.INT64_ARRAY: lambda val: _encode_array_to_bytes(
        [validate_integer_range(v, 64, signed=True) for v in val], "q"
    ),
    DataType.UINT8_ARRAY: lambda val: _encode_array_to_bytes(
        [validate_integer_range(v, 8) for v in val], "B"
    ),
    DataType.UINT16_ARRAY: lambda val: _encode_array_to_bytes(
        [validate_integer_range(v, 16) for v in val], "H"
    ),
    DataType.UINT32_ARRAY: lambda val: _encode_array_to_bytes(
        [validate_integer_range(v, 32) for v in val], "I"
    ),
    DataType.UINT64_ARRAY: lambda val: _encode_array_to_bytes(
        [validate_integer_range(v, 64) for v in val], "Q"
    ),
    # Other types (unchanged)
    DataType.FLOAT: lambda val: val,
    DataType.DOUBLE: lambda val: val,
    DataType.BOOLEAN: lambda val: val,
    DataType.STRING: lambda val: val,
    DataType.DATETIME: lambda val: int(val.timestamp() * 1000),
    DataType.TEXT: lambda val: val,
    DataType.UUID: lambda val: val,
    DataType.BYTES: lambda val: val,
    DataType.FILE: lambda val: val,
    # Other arrays (unchanged)
    DataType.FLOAT_ARRAY: lambda val: _encode_array_to_bytes(val, "f"),
    DataType.DOUBLE_ARRAY: lambda val: _encode_array_to_bytes(val, "d"),
    DataType.BOOLEAN_ARRAY: lambda val: bytes([1 if x else 0 for x in val]),
    DataType.STRING_ARRAY: lambda val: b"\0".join(s.encode("utf-8") for s in val)
    + b"\0",
    DataType.DATETIME_ARRAY: lambda val: _encode_array_to_bytes(
        [int(v.timestamp() * 1000) for v in val], "q"
    ),
}


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
        raise ValueError(
            f"Failed to decode bytes {data} with format {format_char}: {e}"
        )


_decoders = {
    # Unsigned integers
    DataType.UINT8: lambda val: validate_integer_range(val, 8),
    DataType.UINT16: lambda val: validate_integer_range(val, 16),
    DataType.UINT32: lambda val: validate_integer_range(val, 32),
    DataType.UINT64: lambda val: validate_integer_range(val, 64),
    # Signed integers
    DataType.INT8: lambda val: validate_integer_range(val, 8, signed=True),
    DataType.INT16: lambda val: validate_integer_range(val, 16, signed=True),
    DataType.INT32: lambda val: validate_integer_range(val, 32, signed=True),
    DataType.INT64: lambda val: validate_integer_range(val, 64, signed=True),
    # Array decoders - validate after decoding
    DataType.INT8_ARRAY: lambda val: [
        validate_integer_range(v, 8, signed=True)
        for v in _decode_bytes_to_array(val, "b")
    ],
    DataType.INT16_ARRAY: lambda val: [
        validate_integer_range(v, 16, signed=True)
        for v in _decode_bytes_to_array(val, "h")
    ],
    DataType.INT32_ARRAY: lambda val: [
        validate_integer_range(v, 32, signed=True)
        for v in _decode_bytes_to_array(val, "i")
    ],
    DataType.INT64_ARRAY: lambda val: [
        validate_integer_range(v, 64, signed=True)
        for v in _decode_bytes_to_array(val, "q")
    ],
    DataType.UINT8_ARRAY: lambda val: [
        validate_integer_range(v, 8) for v in _decode_bytes_to_array(val, "B")
    ],
    DataType.UINT16_ARRAY: lambda val: [
        validate_integer_range(v, 16) for v in _decode_bytes_to_array(val, "H")
    ],
    DataType.UINT32_ARRAY: lambda val: [
        validate_integer_range(v, 32) for v in _decode_bytes_to_array(val, "I")
    ],
    DataType.UINT64_ARRAY: lambda val: [
        validate_integer_range(v, 64) for v in _decode_bytes_to_array(val, "Q")
    ],
    # Non-integer types (unchanged)
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
    # Array decoders (already updated in previous change)
    DataType.FLOAT_ARRAY: lambda val: _decode_bytes_to_array(val, "f"),
    DataType.DOUBLE_ARRAY: lambda val: _decode_bytes_to_array(val, "d"),
    DataType.BOOLEAN_ARRAY: lambda val: [bool(b) for b in val],
    DataType.STRING_ARRAY: lambda val: [
        s.decode("utf-8") for s in val.split(b"\0") if s
    ],
    DataType.DATETIME_ARRAY: lambda val: [
        datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc)
        for v in _decode_bytes_to_array(val, "q")
    ],
}

"""Module defining the DataType enum"""

import datetime
import enum
import struct
from typing import Sequence, Union

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
    DATASET = 16  #: Unsupported
    BYTES = 17
    FILE = 18
    TEMPLATE = 19  #: Unsupported
    PROPERTYSET = 20  #: Unsupported
    PROPERTYSETLIST = 21  #: Unsupported
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
            raise NotImplementedError(f"{self.name} not implemented") from exc

    def encode(self, value: MetricValue) -> Union[int, float, bool, str, bytes]:
        """Encode a value into the form it should take in a Sparkplug B Protobuf object"""
        try:
            encoder = _encoders[self]
        except KeyError as exc:
            raise NotImplementedError(f"{self.name} not implemented") from exc
        return encoder(value)

    def decode(self, value: Union[int, float, bool, str, bytes]) -> MetricValue:
        """Decode a value from the form it takes in a Sparkplug B Protobuf object"""
        try:
            decoder = _decoders[self]
        except KeyError as exc:
            raise NotImplementedError(f"{self.name} not implemented") from exc
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


def _uint_coder(value: int, bits: int) -> int:
    if not 0 <= value < 2**bits:
        raise OverflowError(f"UInt{bits} overflow with value {value}")
    return value


def _int_encoder(value: int, bits: int) -> int:
    max_val: int = 2 ** (bits - 1)
    if not -max_val <= value < max_val:
        raise OverflowError(f"Int{bits} overflow with value {value}")
    return value + (max_val * 2 if value < 0 else 0)


def _int_decoder(value: int, bits: int) -> int:
    max_val: int = 2**bits
    if not 0 <= value < max_val:
        raise OverflowError(f"Int{bits} overflow with value {value}")
    return value - (max_val if value >= 2 ** (bits - 1) else 0)


def _encode_numeric_array(values: Sequence[float], format_char: str) -> bytes:
    """Convert array to bytes using specified format

    Args:
        values: list of values to encode
        format_char: Format character for struct.pack:
            'b' = int8, 'B' = uint8
            'h' = int16, 'H' = uint16
            'i' = int32, 'I' = uint32
            'q' = int64, 'Q' = uint64
            'f' = float, 'd' = double
    """
    format_str = f"<{len(values)}{format_char}"  # '<' for little endian
    try:
        return struct.pack(format_str, *values)
    except struct.error as exc:
        raise ValueError(f"Failed to encode array with format {format_char}") from exc


def _decode_numeric_array(data: bytes, format_char: str) -> tuple[float, ...]:
    """Convert bytes back to array using specified format

    Args:
        data: Bytes to decode
        format_char: Format character for struct.unpack:
            'b' = int8, 'B' = uint8
            'h' = int16, 'H' = uint16
            'i' = int32, 'I' = uint32
            'q' = int64, 'Q' = uint64
            'f' = float, 'd' = double
    """
    size = struct.calcsize(format_char)
    count = len(data) // size
    format_str = f"<{count}{format_char}"  # '<' for little endian
    try:
        return tuple(struct.unpack(format_str, data))
    except struct.error as exc:
        raise ValueError(f"Failed to decode array with format {format_char}") from exc


def _encode_boolean_array(bools: tuple[bool, ...]) -> bytes:
    num_bits = len(bools)
    num_bytes = (num_bits + 7) // 8

    # 4-byte integer that represents the total number of boolean values
    first_byte = num_bits.to_bytes(4, "little")

    # Form bitstring, right zero pad for the number of bytes
    bitstring = "".join("1" if byte else "0" for byte in bools) + "0" * (
        num_bytes * 8 - num_bits
    )

    # Convert to an integer, handling empty tuple = 0 safely
    int_value = int(bitstring, 2) if bitstring else 0

    # Prepend the first byte with the integer converted to bytes
    return first_byte + int_value.to_bytes(num_bytes, byteorder="big")


def _decode_boolean_array(data: bytes) -> tuple[bool, ...]:
    num_bits = int.from_bytes(data[:4], "little")
    masks = tuple(1 << ind for ind in range(8))[::-1]
    return tuple(bool(byte & mask) for byte in data[4:] for mask in masks)[:num_bits]


_encoders = {
    # Unsigned integers
    DataType.UINT8: lambda val: _uint_coder(val, 8),
    DataType.UINT16: lambda val: _uint_coder(val, 16),
    DataType.UINT32: lambda val: _uint_coder(val, 32),
    DataType.UINT64: lambda val: _uint_coder(val, 64),
    # Signed integers
    DataType.INT8: lambda val: _int_encoder(val, 8),
    DataType.INT16: lambda val: _int_encoder(val, 16),
    DataType.INT32: lambda val: _int_encoder(val, 32),
    DataType.INT64: lambda val: _int_encoder(val, 64),
    # Other scalar types
    DataType.FLOAT: lambda val: val,
    DataType.DOUBLE: lambda val: val,
    DataType.BOOLEAN: lambda val: val,
    DataType.STRING: lambda val: val,
    DataType.DATETIME: lambda val: int(val.timestamp() * 1000),
    DataType.TEXT: lambda val: val,
    DataType.UUID: lambda val: val,
    DataType.BYTES: lambda val: val,
    DataType.FILE: lambda val: val,
    # Numeric arrays
    DataType.INT8_ARRAY: lambda val: _encode_numeric_array(val, "b"),
    DataType.INT16_ARRAY: lambda val: _encode_numeric_array(val, "h"),
    DataType.INT32_ARRAY: lambda val: _encode_numeric_array(val, "i"),
    DataType.INT64_ARRAY: lambda val: _encode_numeric_array(val, "q"),
    DataType.UINT8_ARRAY: lambda val: _encode_numeric_array(val, "B"),
    DataType.UINT16_ARRAY: lambda val: _encode_numeric_array(val, "H"),
    DataType.UINT32_ARRAY: lambda val: _encode_numeric_array(val, "I"),
    DataType.UINT64_ARRAY: lambda val: _encode_numeric_array(val, "Q"),
    DataType.FLOAT_ARRAY: lambda val: _encode_numeric_array(val, "f"),
    DataType.DOUBLE_ARRAY: lambda val: _encode_numeric_array(val, "d"),
    # Other arrays
    DataType.BOOLEAN_ARRAY: _encode_boolean_array,
    DataType.STRING_ARRAY: lambda val: b"\0".join(s.encode("utf-8") for s in val)
    + b"\0",
    DataType.DATETIME_ARRAY: lambda val: _encode_numeric_array(
        tuple(int(v.timestamp() * 1000) for v in val), "Q"
    ),
}

_decoders = {
    # Unsigned integers
    DataType.UINT8: lambda val: _uint_coder(val, 8),
    DataType.UINT16: lambda val: _uint_coder(val, 16),
    DataType.UINT32: lambda val: _uint_coder(val, 32),
    DataType.UINT64: lambda val: _uint_coder(val, 64),
    # Signed integers
    DataType.INT8: lambda val: _int_decoder(val, 8),
    DataType.INT16: lambda val: _int_decoder(val, 16),
    DataType.INT32: lambda val: _int_decoder(val, 32),
    DataType.INT64: lambda val: _int_decoder(val, 64),
    # Other scalar types
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
    # Numeric array
    DataType.INT8_ARRAY: lambda val: _decode_numeric_array(val, "b"),
    DataType.INT16_ARRAY: lambda val: _decode_numeric_array(val, "h"),
    DataType.INT32_ARRAY: lambda val: _decode_numeric_array(val, "i"),
    DataType.INT64_ARRAY: lambda val: _decode_numeric_array(val, "q"),
    DataType.UINT8_ARRAY: lambda val: _decode_numeric_array(val, "B"),
    DataType.UINT16_ARRAY: lambda val: _decode_numeric_array(val, "H"),
    DataType.UINT32_ARRAY: lambda val: _decode_numeric_array(val, "I"),
    DataType.UINT64_ARRAY: lambda val: _decode_numeric_array(val, "Q"),
    DataType.FLOAT_ARRAY: lambda val: _decode_numeric_array(val, "f"),
    DataType.DOUBLE_ARRAY: lambda val: _decode_numeric_array(val, "d"),
    # Other arrays
    DataType.BOOLEAN_ARRAY: _decode_boolean_array,
    DataType.STRING_ARRAY: lambda val: tuple(
        s.decode("utf-8") for s in val.split(b"\0")[:-1]
    ),
    DataType.DATETIME_ARRAY: lambda val: tuple(
        datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc)
        for v in _decode_numeric_array(val, "Q")
    ),
}

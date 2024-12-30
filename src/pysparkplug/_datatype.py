"""Module defining the DataType enum"""

import datetime
import enum
from typing import Union, List, Any, Callable
import struct

from pysparkplug._types import MetricValue

__all__ = ["DataType"]


class DataType(enum.IntEnum):
    """Enumeration of Sparkplug B datatypes"""

    Unknown = 0
    Int8 = 1
    Int16 = 2
    Int32 = 3
    Int64 = 4
    UInt8 = 5
    UInt16 = 6
    UInt32 = 7
    UInt64 = 8
    Float = 9
    Double = 10
    Boolean = 11
    String = 12
    DateTime = 13
    Text = 14
    UUID = 15
    DataSet = 16
    Bytes = 17
    File = 18
    Template = 19
    PropertySet = 20
    PropertySetList = 21
    
    # Array Types - values starting at 22 per Sparkplug B spec
    Int8Array = 22
    Int16Array = 23
    Int32Array = 24
    Int64Array = 25
    UInt8Array = 26
    UInt16Array = 27
    UInt32Array = 28
    UInt64Array = 29
    FloatArray = 30
    DoubleArray = 31
    BooleanArray = 32
    StringArray = 33
    DateTimeArray = 34

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
    DataType.UInt8: "int_value",
    DataType.UInt16: "int_value",
    DataType.UInt32: "int_value",
    DataType.UInt64: "long_value",
    DataType.Int8: "int_value",
    DataType.Int16: "int_value",
    DataType.Int32: "int_value",
    DataType.Int64: "long_value",
    DataType.Float: "float_value",
    DataType.Double: "double_value",
    DataType.Boolean: "boolean_value",
    DataType.String: "string_value",
    DataType.DateTime: "long_value",
    DataType.Text: "string_value",
    DataType.UUID: "string_value",
    DataType.Bytes: "bytes_value",
    DataType.File: "bytes_value",
    DataType.Int8Array: "bytes_value",
    DataType.Int16Array: "bytes_value",
    DataType.Int32Array: "bytes_value",
    DataType.Int64Array: "bytes_value",
    DataType.UInt8Array: "bytes_value",
    DataType.UInt16Array: "bytes_value",
    DataType.UInt32Array: "bytes_value",
    DataType.UInt64Array: "bytes_value",
    DataType.FloatArray: "bytes_value",
    DataType.DoubleArray: "bytes_value",
    DataType.BooleanArray: "bytes_value",
    DataType.StringArray: "bytes_value",
    DataType.DateTimeArray: "bytes_value",
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
    DataType.Int8: lambda val: val,
    DataType.Int16: lambda val: val,
    DataType.Int32: lambda val: val,
    DataType.Int64: lambda val: val,
    DataType.UInt8: lambda val: val,
    DataType.UInt16: lambda val: val,
    DataType.UInt32: lambda val: val,
    DataType.UInt64: lambda val: val,
    DataType.Float: lambda val: val,
    DataType.Double: lambda val: val,
    DataType.Boolean: lambda val: val,
    DataType.String: lambda val: val,
    DataType.DateTime: lambda val: int(val.timestamp() * 1000),
    DataType.Text: lambda val: val,
    DataType.UUID: lambda val: val,
    DataType.Bytes: lambda val: val,
    DataType.File: lambda val: val,
    
    # Array encoders
    DataType.Int8Array: lambda val: _encode_array_to_bytes(val, 'b'),
    DataType.Int16Array: lambda val: _encode_array_to_bytes(val, 'h'),
    DataType.Int32Array: lambda val: _encode_array_to_bytes(val, 'i'),
    DataType.Int64Array: lambda val: _encode_array_to_bytes(val, 'q'),
    DataType.UInt8Array: lambda val: _encode_array_to_bytes(val, 'B'),
    DataType.UInt16Array: lambda val: _encode_array_to_bytes(val, 'H'),
    DataType.UInt32Array: lambda val: _encode_array_to_bytes(val, 'I'),
    DataType.UInt64Array: lambda val: _encode_array_to_bytes(val, 'Q'),
    DataType.FloatArray: lambda val: _encode_array_to_bytes(val, 'f'),
    DataType.DoubleArray: lambda val: _encode_array_to_bytes(val, 'd'),
    DataType.BooleanArray: lambda val: bytes([1 if x else 0 for x in val]),
    DataType.StringArray: lambda val: b'\0'.join(s.encode('utf-8') for s in val) + b'\0',
    DataType.DateTimeArray: lambda val: _encode_array_to_bytes(
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
    DataType.UInt8: lambda val: _uint_coder(val, 8),
    DataType.UInt16: lambda val: _uint_coder(val, 16),
    DataType.UInt32: lambda val: _uint_coder(val, 32),
    DataType.UInt64: lambda val: _uint_coder(val, 64),
    DataType.Int8: lambda val: _int_decoder(val, 8),
    DataType.Int16: lambda val: _int_decoder(val, 16),
    DataType.Int32: lambda val: _int_decoder(val, 32),
    DataType.Int64: lambda val: _int_decoder(val, 64),
    DataType.Float: lambda val: val,
    DataType.Double: lambda val: val,
    DataType.Boolean: lambda val: val,
    DataType.String: lambda val: val,
    DataType.DateTime: lambda val: datetime.datetime.fromtimestamp(
        val * 1e-3, tz=datetime.timezone.utc
    ),
    DataType.Text: lambda val: val,
    DataType.UUID: lambda val: val,
    DataType.Bytes: lambda val: val,
    DataType.File: lambda val: val,
    
    # Array decoders with validation
    DataType.Int8Array: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'b'), 8),
    DataType.Int16Array: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'h'), 16),
    DataType.Int32Array: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'i'), 32),
    DataType.Int64Array: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'q'), 64),
    DataType.UInt8Array: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'B'), 8, signed=False),
    DataType.UInt16Array: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'H'), 16, signed=False),
    DataType.UInt32Array: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'I'), 32, signed=False),
    DataType.UInt64Array: lambda val: _validate_int_array(_decode_bytes_to_array(val, 'Q'), 64, signed=False),
    DataType.FloatArray: lambda val: _decode_bytes_to_array(val, 'f'),
    DataType.DoubleArray: lambda val: _decode_bytes_to_array(val, 'd'),
    DataType.BooleanArray: lambda val: [bool(b) for b in val],
    DataType.StringArray: lambda val: [s.decode('utf-8') for s in val.split(b'\0') if s],
    DataType.DateTimeArray: lambda val: [
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

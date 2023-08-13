"""Module defining the DataType enum"""

import datetime
import enum
from typing import Union

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
    BYTES = 17
    FILE = 18

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
        return encoder(value)  # type: ignore[no-any-return,no-untyped-call]

    def decode(self, value: Union[int, float, bool, str, bytes]) -> MetricValue:
        """Decode a value from the form it takes in a Sparkplug B Protobuf object"""
        try:
            decoder = _decoders[self]
        except KeyError as exc:
            raise ValueError(f"{self} cannot be decoded") from exc
        return decoder(value)  # type: ignore[no-any-return,no-untyped-call]


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
}

_encoders = {
    DataType.UINT8: lambda val: _uint_coder(val, 8),
    DataType.UINT16: lambda val: _uint_coder(val, 16),
    DataType.UINT32: lambda val: _uint_coder(val, 32),
    DataType.UINT64: lambda val: _uint_coder(val, 64),
    DataType.INT8: lambda val: _int_encoder(val, 8),
    DataType.INT16: lambda val: _int_encoder(val, 16),
    DataType.INT32: lambda val: _int_encoder(val, 32),
    DataType.INT64: lambda val: _int_encoder(val, 64),
    DataType.FLOAT: lambda val: val,
    DataType.DOUBLE: lambda val: val,
    DataType.BOOLEAN: lambda val: val,
    DataType.STRING: lambda val: val,
    DataType.DATETIME: lambda val: int(
        val.replace(tzinfo=datetime.timezone.utc).timestamp() * 1e3
    ),
    DataType.TEXT: lambda val: val,
    DataType.UUID: lambda val: val,
    DataType.BYTES: lambda val: val,
    DataType.FILE: lambda val: val,
}

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

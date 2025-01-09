"""Module containing errors and functions to handle them"""

from typing import Optional

from pysparkplug._enums import ConnackCode, ErrorCode

__all__ = ["MQTTError"]


class MQTTError(Exception):
    """Error from MQTT client"""


def check_error_code(
    error_int: int, *, ignore_codes: Optional[set[ErrorCode]] = None
) -> None:
    """Validate error code"""
    if error_int > 0:
        error_code = ErrorCode(error_int)
        if ignore_codes is None or error_code not in ignore_codes:
            raise MQTTError(error_code)


def check_connack_code(
    connack_int: int, *, ignore_codes: Optional[set[ConnackCode]] = None
) -> None:
    """Validate connack code"""
    if connack_int > 0:
        connack_code = ConnackCode(connack_int)
        if ignore_codes is None or connack_code not in ignore_codes:
            raise ConnectionError(connack_code)

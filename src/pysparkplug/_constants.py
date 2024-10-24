"""Module of constants used by the package"""

from typing import Literal

from pysparkplug._types import TypeAlias

SINGLE_LEVEL_WILDCARD_TYPE: TypeAlias = Literal["+"]
SINGLE_LEVEL_WILDCARD: SINGLE_LEVEL_WILDCARD_TYPE = "+"
"""Constant for single-level MQTT topic wildcard

Uses type annotation for compatibility with `Topic` objects.

.. versionadded:: 0.2.0
"""
MULTI_LEVEL_WILDCARD_TYPE: TypeAlias = Literal["#"]
MULTI_LEVEL_WILDCARD: MULTI_LEVEL_WILDCARD_TYPE = "#"
"""Constant for multi-level MQTT topic wildcard

Uses type annotation for compatibility with `Topic` objects.

.. versionadded:: 0.2.0
"""

DEFAULT_CLIENT_PORT = 1883
DEFAULT_CLIENT_KEEPALIVE = 60
DEFAULT_CLIENT_BIND_ADDRESS = ""
DEFAULT_CLIENT_BLOCKING = False

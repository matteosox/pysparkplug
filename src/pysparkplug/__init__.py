"""Initialization code for Sparkplug B package"""

from pysparkplug import _constants, _types
from pysparkplug._client import Client
from pysparkplug._config import ClientOptions, TLSConfig, WSConfig
from pysparkplug._datatype import DataType
from pysparkplug._edge_node import Device, EdgeNode
from pysparkplug._enums import (
    ConnackCode,
    ErrorCode,
    MessageType,
    MQTTProtocol,
    QoS,
    Transport,
)
from pysparkplug._error import MQTTError
from pysparkplug._message import Message
from pysparkplug._metric import Metric
from pysparkplug._payload import (
    DBirth,
    DCmd,
    DData,
    DDeath,
    NBirth,
    NCmd,
    NData,
    NDeath,
    State,
)
from pysparkplug._time import get_current_timestamp
from pysparkplug._topic import Topic
from pysparkplug._version import __version__

__all__ = [
    "Client",
    "ClientOptions",
    "TLSConfig",
    "WSConfig",
    "DataType",
    "Device",
    "EdgeNode",
    "ErrorCode",
    "ConnackCode",
    "MQTTProtocol",
    "QoS",
    "MessageType",
    "Transport",
    "MQTTError",
    "Message",
    "Metric",
    "NBirth",
    "DBirth",
    "NData",
    "DData",
    "NCmd",
    "DCmd",
    "NDeath",
    "DDeath",
    "State",
    "get_current_timestamp",
    "Topic",
    "SINGLE_LEVEL_WILDCARD",
    "MULTI_LEVEL_WILDCARD",
    "MetricValue",
    "__version__",
]

SINGLE_LEVEL_WILDCARD = _constants.SINGLE_LEVEL_WILDCARD
"""Constant for single-level MQTT topic wildcard

Uses type annotation for compatibility with `Topic` objects.

.. versionadded:: 0.2.0
"""

MULTI_LEVEL_WILDCARD = _constants.MULTI_LEVEL_WILDCARD
"""Constant for multi-level MQTT topic wildcard

Uses type annotation for compatibility with `Topic` objects.

.. versionadded:: 0.2.0
"""

MetricValue = _types.MetricValue
"""Type annotation for the types a `Metric`'s `value` attribute can take"""

del _constants, _types

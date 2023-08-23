"""Initialization code for Sparkplug B package"""

from pysparkplug import _constants, _types
from pysparkplug._client import *
from pysparkplug._config import *
from pysparkplug._datatype import *
from pysparkplug._edge_node import *
from pysparkplug._enums import *
from pysparkplug._error import *
from pysparkplug._message import *
from pysparkplug._metric import *
from pysparkplug._payload import *
from pysparkplug._time import *
from pysparkplug._topic import *
from pysparkplug._version import __version__ as __version__

SINGLE_LEVEL_WILDCARD = _constants.SINGLE_LEVEL_WILDCARD
"""Constant for single-level MQTT topic wildcard,
with type annotation for compatibility with pysparkplug interfaces
"""

MULTI_LEVEL_WILDCARD = _constants.MULTI_LEVEL_WILDCARD
"""Constant for multi-level MQTT topic wildcard,
with type annotation for compatibility with pysparkplug interfaces
"""

MetricValue = _types.MetricValue
"""Type annotation for the types a Sparkplug B metric's `value` attribute can take"""

del _constants, _types

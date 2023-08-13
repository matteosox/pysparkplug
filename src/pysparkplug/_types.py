"""Module defining common types"""

import datetime
import sys
from typing import Union

if sys.version_info < (3, 11):
    from typing_extensions import Literal, Protocol, Self, TypeAlias
else:
    from typing import Literal, Protocol, Self, TypeAlias

__all__ = ["Literal", "MetricValue", "Protocol", "Self", "TypeAlias"]

MetricValue: TypeAlias = Union[int, float, bool, str, bytes, datetime.datetime]

"""Module defining common types"""

import datetime
import sys
from typing import Union

if sys.version_info < (3, 11):
    from typing_extensions import Self, TypeAlias
else:
    from typing import Self, TypeAlias

__all__ = ["MetricValue", "Self", "TypeAlias"]

MetricValue: TypeAlias = Union[int, float, bool, str, bytes, datetime.datetime]
"""Type annotation for the types a `Metric`'s `value` attribute can take"""

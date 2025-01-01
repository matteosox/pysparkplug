"""Module defining common types"""

import datetime
import sys
from typing import List, Union

if sys.version_info < (3, 11):
    from typing_extensions import Self, TypeAlias
else:
    from typing import Self, TypeAlias

__all__ = ["MetricValue", "Self", "TypeAlias"]

MetricValue: TypeAlias = Union[
    # Scalar types
    int,
    float,
    bool,
    str,
    bytes,
    datetime.datetime,
    # Array types
    List[int],
    List[float],
    List[bool],
    List[str],
    List[datetime.datetime],
]
"""Type annotation for the types a `Metric`'s `value` attribute can take"""

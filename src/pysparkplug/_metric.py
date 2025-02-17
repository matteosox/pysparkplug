"""Module defining the Metric dataclass"""

import dataclasses
from typing import Optional

from pysparkplug._datatype import DataType
from pysparkplug._metadata import Metadata
from pysparkplug._protobuf import Metric as PB_Metric
from pysparkplug._types import MetricValue, Self

__all__ = ["Metric"]


@dataclasses.dataclass(frozen=True)
class Metric:
    """Class representing a Sparkplug B metric

    Args:
        timestamp:
            timestamp associated with data acquisition time
        name:
            name associated with this metric
        datatype:
            datatype associated with this metric
        value:
            the value of the metric
        alias:
            an integer used to map to the metric's name
        is_historical:
            if this is historical data and should not update real time tag
        is_transient:
            tells consuming clients such as MQTT Engine to not store this as a tag
        is_null:
            if this is null - explicitly say so rather than using -1, false, etc
        metadata:
            optional metadata for this metric
    """

    timestamp: Optional[int]
    name: Optional[str]
    datatype: DataType
    metadata: Optional[Metadata] = None
    value: Optional[MetricValue] = None
    alias: Optional[int] = None
    is_historical: bool = False
    is_transient: bool = False
    is_null: bool = False

    def to_pb(self, include_dtype: bool) -> PB_Metric:  # type: ignore[reportInvalidTypeForm]
        """Returns a Protobuf metric

        Args:
            include_dtype:
                whether or not to include dtypes in the Protobuf metric
        """
        metric = PB_Metric()
        if self.timestamp is not None:
            metric.timestamp = self.timestamp
        if self.name is not None:
            metric.name = self.name
        if include_dtype:
            metric.datatype = self.datatype
        if self.metadata is not None:
            metric.metadata.CopyFrom(self.metadata.to_pb())
        if self.alias is not None:
            metric.alias = self.alias
        if self.is_historical:
            metric.is_historical = self.is_historical
        if self.is_transient:
            metric.is_transient = self.is_transient
        if self.is_null or self.value is None:
            metric.is_null = True
        else:
            setattr(metric, self.datatype.field, self.datatype.encode(self.value))

        return metric

    @classmethod
    def from_pb(cls, metric: PB_Metric) -> Self:  # type: ignore[reportInvalidTypeForm]
        """Constructs a Metric object from a Protobuf metric

        Args:
            metric: the Protobuf metric to construct from

        Returns:
            a Metric object
        """
        datatype = DataType(metric.datatype)
        value_field = metric.WhichOneof("value")
        return cls(
            timestamp=metric.timestamp if metric.HasField("timestamp") else None,
            name=metric.name if metric.HasField("name") else None,
            datatype=datatype,
            value=(
                datatype.decode(getattr(metric, value_field))
                if value_field is not None
                else None
            ),
            alias=metric.alias if metric.HasField("alias") else None,
            is_historical=metric.is_historical,
            is_transient=metric.is_transient,
            is_null=metric.is_null,
            # Check and extract metadata if present
            metadata=Metadata.from_pb(metric.metadata)
            if metric.HasField("metadata")
            else None,
        )

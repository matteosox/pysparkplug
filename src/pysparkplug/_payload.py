"""Module defining the Payload class and its subclasses?"""

from __future__ import annotations

import dataclasses
import json
from abc import abstractmethod
from typing import Optional, Protocol, cast, runtime_checkable

from pysparkplug import _protobuf as protobuf
from pysparkplug._datatype import DataType
from pysparkplug._metric import Metric
from pysparkplug._types import Self

__all__ = [
    "DBirth",
    "DCmd",
    "DData",
    "DDeath",
    "NBirth",
    "NCmd",
    "NData",
    "NDeath",
    "State",
]


@runtime_checkable
class Payload(Protocol):
    """Protocol defining the methods a payload should have"""

    @classmethod
    @abstractmethod
    def decode(cls, raw: bytes, *, birth: Optional[Birth] = None) -> Self:
        """Construct a Payload object from bytes

        Args:
            raw:
                bytes to decode into a Payload object
            birth:
                the Birth object associated with this message,
                for decoding aliases and dropped dtypes

        Returns:
            Payload object
        """
        raise NotImplementedError()

    @abstractmethod
    def encode(self, *, include_dtypes: bool = False) -> bytes:
        """Encode Payload object into bytes

        Args:
            include_dtypes:
                whether or not to include dtypes

        Returns:
            encoded payload in bytes
        """
        raise NotImplementedError()


class _PBPayload:
    @classmethod
    def decode(cls, raw: bytes, *, birth: Optional[Birth] = None) -> Self:
        """Construct a Payload object from bytes

        Args:
            raw:
                bytes to decode into a Payload object
            birth:
                the Birth object associated with this message,
                for decoding aliases and dropped dtypes

        Returns:
            Payload object
        """
        payload = protobuf.Payload.FromString(raw)
        if birth is not None:
            for metric in payload.metrics:
                if not metric.name:
                    metric.name = birth.get_name(metric.alias)
                if metric.datatype == DataType.UNKNOWN:
                    metric.datatype = birth.get_dtype(metric.name)
        if not payload.HasField("timestamp"):
            raise ValueError("Sparkplug payload missing required timestamp field")
        kwargs = {
            "timestamp": payload.timestamp,
            "metrics": tuple(Metric.from_pb(metric) for metric in payload.metrics),
        }
        if payload.HasField("seq"):
            kwargs["seq"] = payload.seq
        return cls(**kwargs)

    def encode(self, *, include_dtypes: bool = False) -> bytes:
        """Encode Payload object into bytes

        Args:
            include_dtypes:
                whether or not to include dtypes

        Returns:
            encoded payload in bytes
        """
        payload = protobuf.Payload()
        payload.timestamp = self.timestamp  # type: ignore[attr-defined]
        if hasattr(self, "seq"):
            payload.seq = self.seq  # type: ignore[reportAttributeAccessIssue]
        payload.metrics.extend(
            metric.to_pb(include_dtype=include_dtypes)
            for metric in self.metrics  # type: ignore[attr-defined]
        )
        return cast(bytes, payload.SerializeToString())


@dataclasses.dataclass(frozen=True)
class Birth(_PBPayload):
    """Class representing a Birth payload

    Args:
        timestamp:
            timestamp at message sending time
        seq:
            sequence number
        metrics:
            metrics associated with this payload
    """

    timestamp: int
    seq: int
    metrics: tuple[Metric, ...]
    _names_mapping: dict[int, str] = dataclasses.field(
        init=False, default_factory=dict, repr=False
    )
    _dtypes_mapping: dict[str, DataType] = dataclasses.field(
        init=False, default_factory=dict, repr=False
    )

    def __post_init__(self) -> None:
        """Validates payload"""
        for metric in self.metrics:
            if metric.name is None:
                raise ValueError(
                    f"Metric {metric} must have a defined name when provided to a Birth payload"
                )
            if metric.datatype == DataType.UNKNOWN:
                raise ValueError(
                    f"Metric {metric} must have a defined datatype when provided to a Birth payload"
                )
            if metric.alias is not None:
                self._names_mapping[metric.alias] = metric.name
            self._dtypes_mapping[metric.name] = metric.datatype

    @classmethod
    def decode(cls, raw: bytes, *, birth: Optional[Birth] = None) -> Self:
        """Construct a Birth object from bytes

        Args:
            raw:
                bytes to decode into a Birth object
            birth:
                unused input since Births payloads are self-contained

        Returns:
            Birth object
        """
        birth = None  # don't use previous birth to determine name/datatypes
        return super().decode(raw, birth=birth)

    def encode(self, *, include_dtypes: bool = False) -> bytes:
        """Encode Birth object into bytes

        Args:
            include_dtypes:
                whether or not to include dtypes

        Returns:
            encoded payload in bytes
        """
        include_dtypes = True  # always include datatypes
        return super().encode(include_dtypes=include_dtypes)

    def get_name(self, alias: int) -> str:
        """Get the name of the metric with the requested alias

        Args:
            alias:
                the alias of the metric we want the name of

        Returns:
            the name of the metric
        """
        return self._names_mapping[alias]

    def get_dtype(self, name: str) -> DataType:
        """Get the dtype of the metric with the requested name

        Args:
            name:
                the name of the metric we want the dtype of

        Returns:
            the dtype of the metric
        """
        return self._dtypes_mapping[name]


class NBirth(Birth):
    """Class representing an NBirth payload

    Args:
        timestamp:
            timestamp at message sending time
        seq:
            sequence number
        metrics:
            metrics associated with this payload
    """


class DBirth(Birth):
    """Class representing a DBirth payload

    Args:
        timestamp:
            timestamp at message sending time
        seq:
            sequence number
        metrics:
            metrics associated with this payload
    """


@dataclasses.dataclass(frozen=True)
class _Data(_PBPayload):
    timestamp: int
    seq: int
    metrics: tuple[Metric, ...]


class NData(_Data):
    """Class representing an NData payload

    Args:
        timestamp:
            timestamp at message sending time
        seq:
            sequence number
        metrics:
            metrics associated with this payload
    """


class DData(_Data):
    """Class representing a DData payload

    Args:
        timestamp:
            timestamp at message sending time
        seq:
            sequence number
        metrics:
            metrics associated with this payload
    """


@dataclasses.dataclass(frozen=True)
class _Cmd(_PBPayload):
    timestamp: int
    metrics: tuple[Metric, ...]


class NCmd(_Cmd):
    """Class representing an NCmd payload

    Args:
        timestamp:
            timestamp at message sending time
        metrics:
            metrics associated with this payload
    """


class DCmd(_Cmd):
    """Class representing a DCmd payload

    Args:
        timestamp:
            timestamp at message sending time
        metrics:
            metrics associated with this payload
    """


@dataclasses.dataclass(frozen=True)
class NDeath:
    """Class representing an NDeath payload

    Args:
        timestamp:
            timestamp at message sending time
        bd_seq_metric:
            birth death sequence number metric
    """

    timestamp: Optional[int]
    bd_seq_metric: Metric

    @classmethod
    def decode(
        cls,
        raw: bytes,
        *,
        birth: Optional[Birth] = None,
    ) -> Self:
        """Construct an NDeath object from bytes

        Args:
            raw:
                bytes to decode into a NDeath object
            birth:
                unused input since NDeaths don't have any metrics with aliases or dropped dtypes

        Returns:
            NDeath object
        """
        payload = protobuf.Payload.FromString(raw)
        return cls(
            timestamp=payload.timestamp if not payload.HasField("timestamp") else None,
            bd_seq_metric=Metric.from_pb(payload.metrics[0]),
        )

    def encode(self, *, include_dtypes: bool = False) -> bytes:
        """Encode NDeath object into bytes

        Args:
            include_dtypes:
                whether or not to include dtypes

        Returns:
            encoded payload in bytes
        """
        include_dtypes = True  # always include datatypes
        payload = protobuf.Payload()
        if self.timestamp is not None:
            payload.timestamp = self.timestamp
        payload.metrics.append(self.bd_seq_metric.to_pb(include_dtype=include_dtypes))
        return cast(bytes, payload.SerializeToString())


@dataclasses.dataclass(frozen=True)
class DDeath:
    """Class representing a DDeath payload

    Args:
        timestamp:
            timestamp at message sending time
        seq:
            sequence number
    """

    timestamp: int
    seq: int

    @classmethod
    def decode(
        cls,
        raw: bytes,
        *,
        birth: Optional[Birth] = None,
    ) -> Self:
        """Construct a DDeath object from bytes

        Args:
            raw:
                bytes to decode into a DDeath object
            birth:
                unused input since DDeaths don't have any metrics

        Returns:
            DDeath object
        """
        payload = protobuf.Payload.FromString(raw)
        return cls(
            timestamp=payload.timestamp,
            seq=payload.seq,
        )

    def encode(self, *, include_dtypes: bool = False) -> bytes:
        """Encode DDeath object into bytes

        Args:
            include_dtypes:
                unused input since DDeaths have no metrics

        Returns:
            encoded payload in bytes
        """
        payload = protobuf.Payload()
        payload.timestamp = self.timestamp
        payload.seq = self.seq
        return cast(bytes, payload.SerializeToString())


@dataclasses.dataclass(frozen=True)
class State:
    """Class representing a State payload

    Args:
        timestamp:
            timestamp at message sending time
        online:
            whether or not the primary host application is online
    """

    timestamp: int
    online: bool

    @classmethod
    def decode(
        cls,
        raw: bytes,
        *,
        birth: Optional[Birth] = None,
    ) -> Self:
        """Construct a State object from bytes

        Args:
            raw:
                bytes to decode into a Payload object
            birth:
                unused input since States don't have any metrics

        Returns:
            State object
        """
        state = json.loads(raw)
        return cls(
            timestamp=state["timestamp"],
            online=state["online"],
        )

    def encode(self, *, include_dtypes: bool = False) -> bytes:
        """Encode State object into bytes

        Args:
            include_dtypes:
                unused input since States have no metrics

        Returns:
            encoded payload in bytes
        """
        return json.dumps({"timestamp": self.timestamp, "online": self.online}).encode()

import dataclasses
from typing import Optional
from pysparkplug._protobuf import MetaData as PB_MetaData
import numpy as np

uint64 = np.uint64

@dataclasses.dataclass(frozen=True)
class Metadata:
    """Class representing a Sparkplug B metric metadata

    Args:
        is_multipart:
            represents whether this metric contains a part of a multipart message
        sequence_number:
            the sequence number associated with a part of a multipart metric
    """

    is_multipart: Optional[bool]
    sequence_number: Optional[int]  # Using 'int' instead of np.uint64 for compatibility

    def to_pb(self) -> PB_MetaData:  # type: ignore
        """Returns a Protobuf Metric's Metadata"""
        metadata = PB_MetaData()
        if self.is_multipart is not None:
            metadata.is_multi_part = self.is_multipart

        if self.sequence_number is not None:
            metadata.seq = self.sequence_number
        return metadata

    @classmethod
    def from_pb(cls, metadata: PB_MetaData):  # type: ignore[reportInvalidTypeForm]
        """Constructs a Metadata object from a Protobuf metadata

        Args:
            metadata: the Protobuf metadata to construct from

        Returns:
            a Metadata object
        """
        return cls(
            is_multipart=metadata.is_multi_part if metadata.HasField("is_multi_part") else None,
            sequence_number=metadata.seq if metadata.HasField("seq") else None,
        )

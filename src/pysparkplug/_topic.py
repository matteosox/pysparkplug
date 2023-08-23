"""Module defining the Topic class"""

import dataclasses
import re
from typing import Optional, Union, cast

from pysparkplug._constants import (
    MULTI_LEVEL_WILDCARD,
    MULTI_LEVEL_WILDCARD_TYPE,
    SINGLE_LEVEL_WILDCARD,
    SINGLE_LEVEL_WILDCARD_TYPE,
)
from pysparkplug._enums import MessageType
from pysparkplug._types import Self, TypeAlias

__all__ = ["Topic"]
WILDCARDS = {SINGLE_LEVEL_WILDCARD, MULTI_LEVEL_WILDCARD}
Wildcard: TypeAlias = Union[SINGLE_LEVEL_WILDCARD_TYPE, MULTI_LEVEL_WILDCARD_TYPE]


@dataclasses.dataclass(frozen=True)
class Topic:
    """Class representing a Sparkplug B topic

    Args:
        group_id:
            the Group ID element of the topic namespace provides for a logical
            grouping of Sparkplug Edge Nodes into the MQTT Server and back out
            to the consuming Sparkplug Host Applications
        message_type:
            the message_type element of the topic namespace provides an
            indication as to how to handle the MQTT payload of the message
        edge_node_id:
            the edge_node_id element of the Sparkplug topic namespace uniquely
            identifies the Sparkplug Edge Node within the infrastructure
        device_id:
            the device_id element of the Sparkplug topic namespace identifies
            a device attached (physically or logically) to the Sparkplug Edge
            Node
        sparkplug_host_id:
            the unique identifier of the Sparkplug Host Application
    """

    namespace = "spBv1.0"
    group_id: Optional[str] = None
    message_type: Optional[Union[MessageType, Wildcard]] = None
    edge_node_id: Optional[str] = None
    device_id: Optional[str] = None
    sparkplug_host_id: Optional[str] = None

    _validator = re.compile(f"[/{SINGLE_LEVEL_WILDCARD}{MULTI_LEVEL_WILDCARD}]")

    def __post_init__(self) -> None:
        if (
            self.message_type is not None
            and self.message_type not in WILDCARDS
            and self._validator.search(self.message_type) is not None
        ):
            raise ValueError(
                f"message_type {self.message_type} cannot contain /, "
                f"{SINGLE_LEVEL_WILDCARD}, or {MULTI_LEVEL_WILDCARD} characters"
            )
        if (
            self.group_id is not None
            and self.group_id not in WILDCARDS
            and self._validator.search(self.group_id) is not None
        ):
            raise ValueError(
                f"group_id {self.group_id} cannot contain /, "
                f"{SINGLE_LEVEL_WILDCARD}, or {MULTI_LEVEL_WILDCARD} characters"
            )
        if (
            self.edge_node_id is not None
            and self.edge_node_id not in WILDCARDS
            and self._validator.search(self.edge_node_id) is not None
        ):
            raise ValueError(
                f"edge_node_id {self.edge_node_id} cannot contain /, "
                f"{SINGLE_LEVEL_WILDCARD}, or {MULTI_LEVEL_WILDCARD} characters"
            )
        if (
            self.device_id is not None
            and self.device_id not in WILDCARDS
            and self._validator.search(self.device_id) is not None
        ):
            raise ValueError(
                f"device_id {self.device_id} cannot contain /, "
                f"{SINGLE_LEVEL_WILDCARD}, or {MULTI_LEVEL_WILDCARD} characters"
            )
        if (
            self.sparkplug_host_id is not None
            and self.sparkplug_host_id not in WILDCARDS
            and self._validator.search(self.sparkplug_host_id) is not None
        ):
            raise ValueError(
                f"sparkplug_host_id {self.sparkplug_host_id} cannot contain /, "
                f"{SINGLE_LEVEL_WILDCARD}, or {MULTI_LEVEL_WILDCARD} characters"
            )

    @classmethod
    def from_str(cls, topic: str) -> Self:
        """Construct a Topic object from a topic string

        Args:
            topic: the Sparkplug B topic in raw string form

        Returns:
            a Topic object
        """
        parts = topic.split("/")
        namespace = parts[0]
        if namespace != cls.namespace:
            raise ValueError(f"Topic with invalid namespace {namespace}")
        if parts[1] == MessageType.STATE:
            return cls(message_type=MessageType.STATE, sparkplug_host_id=parts[2])

        group_id = None
        message_type = None
        edge_node_id = None
        device_id = None

        try:
            group_id = parts[1]
            message_type = cast(
                Union[MessageType, Wildcard],
                parts[2] if parts[2] in WILDCARDS else MessageType(parts[2]),
            )
            edge_node_id = parts[3]
            device_id = parts[4]
        except IndexError:
            pass
        return cls(
            group_id=group_id,
            message_type=message_type,
            edge_node_id=edge_node_id,
            device_id=device_id,
        )

    def __str__(self) -> str:
        """Encode a Topic object as a string"""
        if self.message_type == MessageType.STATE:
            return f"{self.namespace}/{self.message_type}/{self.sparkplug_host_id}"
        if self.device_id is not None:
            return f"{self.namespace}/{self.group_id}/{self.message_type}/{self.edge_node_id}/{self.device_id}"
        if self.edge_node_id is not None:
            return f"{self.namespace}/{self.group_id}/{self.message_type}/{self.edge_node_id}"
        if self.message_type is not None:
            return f"{self.namespace}/{self.group_id}/{self.message_type}"
        return f"{self.namespace}/{self.group_id}"

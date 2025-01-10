"""Module defining the EdgeNode & Device classes"""

from __future__ import annotations

import itertools
import logging
from typing import Callable, Iterable, Optional

from pysparkplug._client import Client
from pysparkplug._constants import (
    DEFAULT_CLIENT_BIND_ADDRESS,
    DEFAULT_CLIENT_BLOCKING,
    DEFAULT_CLIENT_KEEPALIVE,
    DEFAULT_CLIENT_PORT,
)
from pysparkplug._datatype import DataType
from pysparkplug._enums import MessageType, QoS
from pysparkplug._message import Message
from pysparkplug._metric import Metric
from pysparkplug._payload import DBirth, DData, DDeath, NBirth, NData, NDeath
from pysparkplug._time import get_current_timestamp
from pysparkplug._topic import Topic
from pysparkplug._types import Self

__all__ = ["Device", "EdgeNode"]
logger = logging.getLogger(__name__)
BD_SEQ = "bdSeq"
SEQ_LIMIT = 256


def _default_cmd_callback(_: EdgeNode, message: Message) -> None:
    logger.info(f"Received command {message}")


class EdgeNode:
    """Class representing an EdgeNode in Sparkplug B

    Args:
        group_id:
            the Group ID element of the topic namespace provides for a logical
            grouping of Sparkplug Edge Nodes into the MQTT Server and back out
            to the consuming Sparkplug Host Applications
        edge_node_id:
            the edge_node_id element of the Sparkplug topic namespace uniquely
            identifies the Sparkplug Edge Node within the infrastructure
        metrics:
            the metrics associated with this edge node
        client:
            the low-level MQTT client used by this edge node for connecting to
            the broker
        cmd_callback:
            the callback function to execute when an NCMD payload is received
    """

    group_id: str
    edge_node_id: str
    _metrics: dict[str, Metric]
    _devices: dict[str, Device]
    _client: Client

    _bd_seq_metric: Metric
    __seq_cycler: itertools.cycle[int] = itertools.cycle(range(SEQ_LIMIT))
    __bd_seq_cycler: itertools.cycle[int] = itertools.cycle(range(SEQ_LIMIT))
    _connected: bool = False

    def __init__(
        self,
        group_id: str,
        edge_node_id: str,
        metrics: Iterable[Metric],
        client: Optional[Client] = None,
        cmd_callback: Callable[[Self, Message], None] = _default_cmd_callback,
    ):
        self.group_id = group_id
        self.edge_node_id = edge_node_id
        self._setup_metrics(metrics)
        self._devices = {}
        self._client = client if client is not None else Client()

        # Subscribe to NCMD
        n_cmd_topic = Topic(
            message_type=MessageType.NCMD,
            group_id=self.group_id,
            edge_node_id=self.edge_node_id,
        )
        self.subscribe(
            topic=n_cmd_topic,
            qos=QoS.AT_LEAST_ONCE,
            callback=lambda _, message: cmd_callback(self, message),
        )

    def _setup_metrics(self, metrics: Iterable[Metric]) -> None:
        self._metrics = {}
        for metric in metrics:
            if metric.name is None:
                raise ValueError(
                    f"Metric {metric} must have a defined name when provided to an Edge Node"
                )
            if metric.datatype == DataType.UNKNOWN:
                raise ValueError(
                    f"Metric {metric} must have a defined datatype when provided to an Edge Node"
                )
            self._metrics[metric.name] = metric

    def _setup_will(self) -> None:
        """Set the bdSeq metric and set the will with an NDEATH message with
        that metric for the next time we connect.
        """
        self._bd_seq_metric = Metric(
            timestamp=get_current_timestamp(),
            name=BD_SEQ,
            datatype=DataType.INT64,
            value=self._bd_seq,
        )
        will_topic = Topic(
            message_type=MessageType.NDEATH,
            group_id=self.group_id,
            edge_node_id=self.edge_node_id,
        )
        will_payload = NDeath(
            timestamp=get_current_timestamp(), bd_seq_metric=self._bd_seq_metric
        )
        will_message = Message(
            topic=will_topic, payload=will_payload, qos=QoS.AT_MOST_ONCE, retain=False
        )
        self._client.set_will(will_message)

    def connect(
        self,
        host: str,
        *,
        port: int = DEFAULT_CLIENT_PORT,
        keepalive: int = DEFAULT_CLIENT_KEEPALIVE,
        bind_address: str = DEFAULT_CLIENT_BIND_ADDRESS,
        blocking: bool = DEFAULT_CLIENT_BLOCKING,
    ) -> None:
        """Connect edge node to the broker

        Args:
            host:
                the hostname or IP address of the remote broker
            port:
                the port of the broker
            keepalive:
                maximum period in seconds allowed between communications with the broker
            bind_address:
                the IP address of a local network interface to bind this client to, assuming multiple interfaces exist
            blocking:
                whether or not to connect in a blocking way, or connect with a separate thread
        """

        # Setup will for next connection
        self._setup_will()

        def callback(client: Client) -> None:
            self._connected = True
            # Reset seq cycler
            self.__seq_cycler = itertools.cycle(range(SEQ_LIMIT))

            # Publish NBIRTH
            n_birth_topic = Topic(
                message_type=MessageType.NBIRTH,
                group_id=self.group_id,
                edge_node_id=self.edge_node_id,
            )
            metrics = (*self._metrics.values(), self._bd_seq_metric)
            n_birth = NBirth(
                timestamp=get_current_timestamp(), seq=self._seq, metrics=metrics
            )
            client.publish(
                Message(
                    topic=n_birth_topic,
                    payload=n_birth,
                    qos=QoS.AT_MOST_ONCE,
                    retain=False,
                ),
                include_dtypes=True,
            )

            # Publish DBIRTHs
            for device in self._devices.values():
                d_birth_topic = Topic(
                    message_type=MessageType.DBIRTH,
                    group_id=self.group_id,
                    edge_node_id=self.edge_node_id,
                    device_id=device.device_id,
                )
                d_birth = DBirth(
                    timestamp=get_current_timestamp(),
                    seq=self._seq,
                    metrics=tuple(device.metrics.values()),
                )
                client.publish(
                    Message(
                        topic=d_birth_topic,
                        payload=d_birth,
                        qos=QoS.AT_MOST_ONCE,
                        retain=False,
                    ),
                    include_dtypes=True,
                )

            # Setup will for next connection
            self._setup_will()

        self._client.connect(
            host,
            port=port,
            keepalive=keepalive,
            bind_address=bind_address,
            blocking=blocking,
            callback=callback,
        )

    def disconnect(self) -> None:
        """Disconnect from the broker cleanly."""
        if self._connected:
            n_death_topic = Topic(
                message_type=MessageType.NDEATH,
                group_id=self.group_id,
                edge_node_id=self.edge_node_id,
            )
            n_death = NDeath(
                timestamp=get_current_timestamp(), bd_seq_metric=self._bd_seq_metric
            )
            ndeath_message = Message(
                topic=n_death_topic, payload=n_death, qos=QoS.AT_MOST_ONCE, retain=False
            )
            self._client.publish(ndeath_message)

        self._client.disconnect()
        self._connected = False

    def register(self, device: Device) -> None:
        """Register a device to the edge node, can be run while edge node is connected

        Args:
            device:
                the device to register to the edge node
        """
        if device.device_id in self._devices:
            raise ValueError(
                f"Cannot register device with id {device.device_id} as another device "
                "is already registered with this edge node with that id"
            )
        self._devices[device.device_id] = device
        d_cmd_topic = Topic(
            message_type=MessageType.DCMD,
            group_id=self.group_id,
            edge_node_id=self.edge_node_id,
            device_id=device.device_id,
        )
        self.subscribe(
            topic=d_cmd_topic,
            qos=QoS.AT_LEAST_ONCE,
            callback=lambda _, message: device.cmd_callback(self, message),
        )
        if self._connected:
            d_birth_topic = Topic(
                message_type=MessageType.DBIRTH,
                group_id=self.group_id,
                edge_node_id=self.edge_node_id,
                device_id=device.device_id,
            )
            d_birth = DBirth(
                timestamp=get_current_timestamp(),
                seq=self._seq,
                metrics=tuple(device.metrics.values()),
            )
            self._client.publish(
                Message(
                    topic=d_birth_topic,
                    payload=d_birth,
                    qos=QoS.AT_MOST_ONCE,
                    retain=False,
                ),
                include_dtypes=True,
            )

    def deregister(self, device_id: str) -> None:
        """Remove a device from the edge node, sending a DDeath if the edge node is online.

        Args:
            device_id: the id of the device to be deregistered
        """
        try:
            del self._devices[device_id]
        except KeyError as exc:
            raise ValueError(
                f"Cannot deregister device with id {device_id} as no device with that "
                "id is registered with this edge node"
            ) from exc

        if self._connected:
            d_death_topic = Topic(
                message_type=MessageType.DDEATH,
                group_id=self.group_id,
                edge_node_id=self.edge_node_id,
                device_id=device_id,
            )
            d_death = DDeath(
                timestamp=get_current_timestamp(),
                seq=self._seq,
            )
            self._client.publish(
                Message(
                    topic=d_death_topic,
                    payload=d_death,
                    qos=QoS.AT_MOST_ONCE,
                    retain=False,
                ),
                include_dtypes=True,
            )

        d_cmd_topic = Topic(
            message_type=MessageType.DCMD,
            group_id=self.group_id,
            edge_node_id=self.edge_node_id,
            device_id=device_id,
        )
        self.unsubscribe(d_cmd_topic)

    def subscribe(
        self,
        topic: Topic,
        qos: QoS,
        callback: Callable[[Self, Message], None],
    ) -> None:
        """Subscribe to the specified topic

        Args:
            topic:
                the topic to be subscribed to
            qos:
                the qos of the subscription
            callback:
                the callback to run when messages are received for this subscription
        """

        def cb(
            _client: Client,
            message: Message,
        ) -> None:
            callback(self, message)

        self._client.subscribe(topic, qos, cb)

    def unsubscribe(self, topic: Topic) -> None:
        """Unsubscribe from the specified topic

        Args:
            topic:
                the topic to be subscribed to
        """
        self._client.unsubscribe(topic)

    @property
    def metrics(self) -> dict[str, Metric]:
        """Returns a copy of the metrics for this edge node in a dictionary"""
        return self._metrics.copy()

    @property
    def devices(self) -> dict[str, Device]:
        """Returns a copy of the devices for this edge node in a dictionary"""
        return self._devices.copy()

    def update(self, metrics: Iterable[Metric]) -> None:
        """Update some (or all) of the edge node's metrics

        Args:
            metrics:
                an iterable of metrics to be updated
        """
        for metric in metrics:
            if metric.name is None:
                raise ValueError(
                    f"Metric {metric} must have a defined name when provided to an Edge Node"
                )
            try:
                curr_metric = self._metrics[metric.name]
            except KeyError as exc:
                raise ValueError(
                    f"Unrecognized metric {metric.name} cannot be updated"
                ) from exc
            if curr_metric.datatype != metric.datatype:
                raise ValueError(
                    f"Metric datatype provided {metric.datatype} "
                    f"doesn't match {curr_metric.datatype}"
                )
            self._metrics[metric.name] = metric

        topic = Topic(
            message_type=MessageType.NDATA,
            group_id=self.group_id,
            edge_node_id=self.edge_node_id,
        )
        n_data = NData(
            timestamp=get_current_timestamp(), seq=self._seq, metrics=tuple(metrics)
        )
        self._client.publish(
            Message(topic=topic, payload=n_data, qos=QoS.AT_MOST_ONCE, retain=False),
            include_dtypes=True,
        )

    def update_device(self, device_id: str, metrics: Iterable[Metric]) -> None:
        """Update some (or all) of the metrics associated with the provided device_id

        Args:
            device_id:
                the id of the device to be updated
            metrics:
                an iterable of metrics to be updated
        """
        try:
            device = self._devices[device_id]
        except KeyError as exc:
            raise ValueError(
                f"Unable to update device {device_id} as no device with that id is "
                "registered to this edge node"
            ) from exc
        device.update(metrics)
        d_data_topic = Topic(
            message_type=MessageType.DDATA,
            group_id=self.group_id,
            edge_node_id=self.edge_node_id,
            device_id=device_id,
        )
        d_data = DData(get_current_timestamp(), seq=self._seq, metrics=tuple(metrics))
        self._client.publish(
            Message(
                topic=d_data_topic, payload=d_data, qos=QoS.AT_MOST_ONCE, retain=False
            ),
            include_dtypes=True,
        )

    @property
    def _seq(self) -> int:
        return next(self.__seq_cycler)

    @property
    def _bd_seq(self) -> int:
        return next(self.__bd_seq_cycler)


class Device:
    """Class representing a Device in Sparkplug B

    Args:
        device_id:
            the device_id element of the Sparkplug topic namespace identifies
            a device attached (physically or logically) to the Sparkplug Edge
            Node
        metrics:
            the metrics associated with this device
        cmd_callback:
            the callback function to execute when a DCMD payload is received
    """

    device_id: str
    _metrics: dict[str, Metric]
    cmd_callback: Callable[[EdgeNode, Message], None]

    def __init__(
        self,
        device_id: str,
        metrics: Iterable[Metric],
        cmd_callback: Callable[[EdgeNode, Message], None] = _default_cmd_callback,
    ):
        self.device_id = device_id
        self._setup_metrics(metrics)
        self.cmd_callback = cmd_callback

    def _setup_metrics(self, metrics: Iterable[Metric]) -> None:
        self._metrics = {}
        for metric in metrics:
            if metric.name is None:
                raise ValueError(
                    f"Metric {metric} must have a defined name when provided to an Edge Node"
                )
            if metric.datatype == DataType.UNKNOWN:
                raise ValueError(
                    f"Metric {metric} must have a defined datatype when provided to an Edge Node"
                )
            self._metrics[metric.name] = metric

    @property
    def metrics(self) -> dict[str, Metric]:
        """Returns a copy of the metrics for this edge node in a dictionary"""
        return self._metrics.copy()

    def update(self, metrics: Iterable[Metric]) -> None:
        """Update some (or all) of the device's metrics

        Args:
            metrics:
                an iterable of metrics to be updated
        """
        for metric in metrics:
            if metric.name is None:
                raise ValueError(
                    f"Metric {metric} must have a defined name when provided to a Device"
                )
            try:
                curr_metric = self._metrics[metric.name]
            except KeyError as exc:
                raise ValueError(
                    f"Unrecognized metric {metric.name} cannot be updated"
                ) from exc
            if curr_metric.datatype != metric.datatype:
                raise ValueError(
                    f"Metric datatype provided {metric.datatype} "
                    f"doesn't match {curr_metric.datatype}"
                )
            self._metrics[metric.name] = metric

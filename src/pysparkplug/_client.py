"""Module containing the low-level Sparkplug B client"""

import logging
from typing import Any, Callable, Optional, Union

from paho.mqtt import client as paho_mqtt

from pysparkplug._config import ClientOptions, TLSConfig, WSConfig
from pysparkplug._constants import (
    DEFAULT_CLIENT_BIND_ADDRESS,
    DEFAULT_CLIENT_BLOCKING,
    DEFAULT_CLIENT_KEEPALIVE,
    DEFAULT_CLIENT_PORT,
)
from pysparkplug._enums import ErrorCode, MQTTProtocol, QoS, Transport
from pysparkplug._error import check_connack_code, check_error_code
from pysparkplug._message import Message
from pysparkplug._payload import Birth
from pysparkplug._topic import Topic
from pysparkplug._types import Self

__all__ = ["Client"]
logger = logging.getLogger(__name__)


class Client:
    """Low-level MQTT client

    Args:
        client_id:
            the unique client id string used when connecting to the broker
        protocol:
            the version of the MQTT protocol to use for this client
        username:
            the username used for broker authentication
        password:
            the password used for broker authentication
        transport_config:
            a config object defining the transport layer protocol the
            client will use to connect to the broker
        client_options:
            a config object defining various options for the client
    """

    _client: paho_mqtt.Client
    _subscriptions: dict[Topic, QoS]
    _births: dict[tuple[Optional[str], Optional[str], Optional[str]], Birth]

    def __init__(
        self,
        client_id: Optional[str] = None,
        protocol: MQTTProtocol = MQTTProtocol.MQTT_V311,
        username: Optional[str] = None,
        password: Optional[str] = None,
        transport_config: Optional[Union[TLSConfig, WSConfig]] = None,
        client_options: ClientOptions = ClientOptions(),
    ) -> None:
        self._client = paho_mqtt.Client(
            client_id=client_id,  # type: ignore[reportArgumentType]
            clean_session=True,
            protocol=protocol,
            transport=(
                Transport.WS
                if isinstance(transport_config, WSConfig)
                else Transport.TCP
            ),
            reconnect_on_failure=client_options.reconnect_on_failure,
        )
        self._client.enable_logger(logger)
        if username is not None:
            self._client.username_pw_set(username=username, password=password)
        if isinstance(transport_config, TLSConfig):
            self._client.tls_set(
                ca_certs=transport_config.ca_certs,
                certfile=transport_config.certfile,
                keyfile=transport_config.keyfile,
                cert_reqs=transport_config.cert_reqs,
                tls_version=transport_config.tls_version,
                ciphers=transport_config.ciphers,
            )
        elif isinstance(transport_config, WSConfig):
            self._client.ws_set_options(
                path=transport_config.path,
                headers=transport_config.headers,
            )
        elif transport_config is not None:
            raise TypeError(f"Unrecognized transport_config type {transport_config}")
        self._client.max_inflight_messages_set(
            inflight=client_options.max_inflight_messages
        )
        self._client.max_queued_messages_set(
            queue_size=client_options.max_queued_messages
        )
        self._client.message_retry_set(retry=client_options.message_retry_timeout)
        self._client.reconnect_delay_set(
            min_delay=client_options.reconnection_delay_min,
            max_delay=client_options.reconnection_delay_max,
        )
        self._births = {}
        self._subscriptions = {}

    def set_will(self, message: Optional[Message]) -> None:
        """Set the last will & testament for the specified message

        Args:
            message:
                the message to be registered with the broker, or None, which clears the will
        """
        if message is None:
            self._client.will_clear()
        else:
            self._client.will_set(
                topic=str(message.topic),
                payload=message.payload.encode(),
                qos=message.qos,
                retain=message.retain,
            )

    def connect(
        self,
        host: str,
        *,
        port: int = DEFAULT_CLIENT_PORT,
        keepalive: int = DEFAULT_CLIENT_KEEPALIVE,
        bind_address: str = DEFAULT_CLIENT_BIND_ADDRESS,
        blocking: bool = DEFAULT_CLIENT_BLOCKING,
        callback: Optional[Callable[[Self], None]] = None,
    ) -> None:
        """Connect client to the broker

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
            callback:
                a custom callback to be called each time the client successfully connects
        """

        def cb(
            _client: paho_mqtt.Client,
            _userdata: dict[Any, Any],
            _flags: dict[Any, Any],
            rc: int,
        ) -> None:
            self._on_connect(rc)
            if callback is not None:
                callback(self)

        self._client.on_connect = cb
        self._client.connect(
            host=host,
            port=port,
            keepalive=keepalive,
            bind_address=bind_address,
        )
        if blocking:
            self._client.loop_forever()
        else:
            self._client.loop_start()

    def _on_connect(self, rc: int) -> None:
        check_connack_code(rc)
        self._births.clear()
        for topic, qos in list(self._subscriptions.items()):
            self._subscribe(topic=topic, qos=qos)

    def disconnect(self) -> None:
        """Disconnect from the broker cleanly, i.e. results in no
        will message being sent by the broker.
        """
        self._client.disconnect()
        self._client.loop_stop()  # stop loop, even if we were running in blocking mode

    def publish(
        self,
        message: Message,
        *,
        include_dtypes: bool = False,
    ) -> None:
        """Publish a message to the broker

        Args:
            message:
                the message to be published
            include_dtypes:
                whether or not to include the dtypes of the message
        """
        result = self._client.publish(
            topic=str(message.topic),
            payload=message.payload.encode(include_dtypes=include_dtypes),
            qos=message.qos,
            retain=message.retain,
        )
        check_error_code(result.rc)

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
            _client: paho_mqtt.Client,
            _userdata: dict[Any, Any],
            mqtt_message: paho_mqtt.MQTTMessage,
        ) -> None:
            message = self._handle_message(mqtt_message)
            callback(self, message)

        self._client.message_callback_add(str(topic), cb)
        self._subscriptions[topic] = qos
        self._subscribe(topic, qos)

    def _handle_message(self, mqtt_message: paho_mqtt.MQTTMessage) -> Message:
        topic = Topic.from_str(mqtt_message.topic)
        key = (topic.group_id, topic.edge_node_id, topic.device_id)
        birth = self._births.get(key)
        message = Message.from_mqtt_message(mqtt_message, birth=birth)
        if isinstance(message.payload, Birth):
            self._births[key] = message.payload

        return message

    def _subscribe(self, topic: Topic, qos: QoS) -> None:
        result, _ = self._client.subscribe(str(topic), qos)
        check_error_code(result, ignore_codes={ErrorCode.NO_CONN})

    def unsubscribe(self, topic: Topic) -> None:
        """Unsubscribe from the specified topic

        Args:
            topic:
                the topic to be subscribed to
        """
        result, _ = self._client.unsubscribe(str(topic))
        check_error_code(result)
        del self._subscriptions[topic]
        self._client.message_callback_remove(str(topic))

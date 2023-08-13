"""Module defining the Message class"""

import dataclasses
from typing import Optional

from paho.mqtt import client as paho_mqtt

from pysparkplug._enums import QoS
from pysparkplug._payload import Birth, Payload
from pysparkplug._topic import Topic
from pysparkplug._types import Self

__all__ = ["Message"]


@dataclasses.dataclass(frozen=True)
class Message:
    """Class representing a Sparkplug B message

    Args:
        topic:
            the Sparkplug B topic associated with this message
        payload:
            the Sparkplug B payload associated with this message
        qos:
            the MQTT quality of service associated with this message
        retain:
            if set to True, the message will be set as the
            "last known good"/retained message for the topic
    """

    topic: Topic
    payload: Payload
    qos: QoS
    retain: bool

    @classmethod
    def from_mqtt_message(
        cls, mqtt_message: paho_mqtt.MQTTMessage, *, birth: Optional[Birth] = None
    ) -> Self:
        """Constructs a Message object from a Paho MQTTMessage object

        Args:
            mqtt_message:
                the Paho MQTTMessage object to construct from
            birth:
                the Birth object associated with this message,
                for decoding aliases and dropped dtypes
        """
        topic = Topic.from_str(mqtt_message.topic)
        # We have to ignore some mypy here since we know that mqtt gives us a
        # fully defined topic, i.e. no wildcards.
        return cls(
            topic=topic,
            payload=topic.message_type.payload.decode(  # type: ignore[union-attr]
                mqtt_message.payload, birth=birth
            ),
            qos=QoS(mqtt_message.qos),
            retain=mqtt_message.retain,
        )

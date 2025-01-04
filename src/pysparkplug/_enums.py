"""Enumerations for MQTT and Sparkplug B"""

import enum

from pysparkplug import _payload as payload
from pysparkplug._strenum import StrEnum

__all__ = [
    "ConnackCode",
    "ErrorCode",
    "MQTTProtocol",
    "MessageType",
    "QoS",
    "Transport",
]


class ErrorCode(enum.IntEnum):
    """MQTT error codes"""

    AGAIN = -1
    SUCCESS = 0
    NOMEM = 1
    PROTOCOL = 2
    INVAL = 3
    NO_CONN = 4
    CONN_REFUSED = 5
    NOT_FOUND = 6
    CONN_LOST = 7
    TLS = 8
    PAYLOAD_SIZE = 9
    NOT_SUPPORTED = 10
    AUTH = 11
    ACL_DENIED = 12
    UNKNOWN = 13
    ERRNO = 14
    QUEUE_SIZE = 15
    KEEPALIVE = 16

    def __str__(self) -> str:
        return _error_strings.get(self, "Unkown error")


_error_strings = {
    ErrorCode.SUCCESS: "No error",
    ErrorCode.NOMEM: "Out of memory",
    ErrorCode.PROTOCOL: "A network protocol error occurred when communicating with the broker",
    ErrorCode.INVAL: "Invalid function arguments provided",
    ErrorCode.NO_CONN: "The client is not currently connected",
    ErrorCode.CONN_REFUSED: "The connection was refused",
    ErrorCode.NOT_FOUND: "Message not found (internal error)",
    ErrorCode.CONN_LOST: "The connection was lost",
    ErrorCode.TLS: "A TLS error occurred",
    ErrorCode.PAYLOAD_SIZE: "Payload too large",
    ErrorCode.NOT_SUPPORTED: "This feature is not supported",
    ErrorCode.AUTH: "Authorisation failed",
    ErrorCode.ACL_DENIED: "Access denied by ACL",
    ErrorCode.UNKNOWN: "Unknown error",
    ErrorCode.ERRNO: "Error defined by errno",
    ErrorCode.QUEUE_SIZE: "Message queue full",
    ErrorCode.KEEPALIVE: "Client or broker did not communicate in the keepalive interval",
}


class ConnackCode(enum.IntEnum):
    """MQTT Connection Acknowledgement codes"""

    CONNACK_ACCEPTED = 0
    CONNACK_REFUSED_PROTOCOL_VERSION = 1
    CONNACK_REFUSED_IDENTIFIER_REJECTED = 2
    CONNACK_REFUSED_SERVER_UNAVAILABLE = 3
    CONNACK_REFUSED_BAD_USERNAME_PASSWORD = 4
    CONNACK_REFUSED_NOT_AUTHORIZED = 5

    def __str__(self) -> str:
        return _connack_strings.get(self, "Connection Refused: unknown reason")


_connack_strings = {
    ConnackCode.CONNACK_ACCEPTED: "Connection accepted",
    ConnackCode.CONNACK_REFUSED_PROTOCOL_VERSION: "Connection refused: unacceptable protocol version",
    ConnackCode.CONNACK_REFUSED_IDENTIFIER_REJECTED: "Connection refused: identifier rejected",
    ConnackCode.CONNACK_REFUSED_SERVER_UNAVAILABLE: "Connection refused: broker unavailable",
    ConnackCode.CONNACK_REFUSED_BAD_USERNAME_PASSWORD: "Connection refused: bad user name or password",
    ConnackCode.CONNACK_REFUSED_NOT_AUTHORIZED: "Connection refused: not authorised",
}


class QoS(enum.IntEnum):
    """MQTT quality of service enum"""

    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2


class MQTTProtocol(enum.IntEnum):
    """MQTT protocol enum"""

    MQTT_V31 = 3
    MQTT_V311 = 4
    MQTT_V5 = 5


class Transport(StrEnum):
    """MQTT transport enum"""

    WS = "websockets"
    TCP = "tcp"


class MessageType(StrEnum):
    """Sparkplug B message type enum"""

    STATE = "STATE"
    NBIRTH = "NBIRTH"
    NDATA = "NDATA"
    NCMD = "NCMD"
    NDEATH = "NDEATH"
    DBIRTH = "DBIRTH"
    DDATA = "DDATA"
    DCMD = "DCMD"
    DDEATH = "DDEATH"

    @property
    def payload(self) -> type:
        """Returns the payload class for this message type"""
        return _payloads[self]


_payloads = {
    MessageType.STATE: payload.State,
    MessageType.NBIRTH: payload.NBirth,
    MessageType.DBIRTH: payload.DBirth,
    MessageType.NDATA: payload.NData,
    MessageType.DDATA: payload.DData,
    MessageType.NCMD: payload.NCmd,
    MessageType.DCMD: payload.DCmd,
    MessageType.NDEATH: payload.NDeath,
    MessageType.DDEATH: payload.DDeath,
}

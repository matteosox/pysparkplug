"""Configuration classes for MQTT and Sparkplug B"""

import dataclasses
import ssl
from typing import Any, Callable, Optional, Union

__all__ = [
    "ClientOptions",
    "TLSConfig",
    "WSConfig",
]


@dataclasses.dataclass(frozen=True)
class TLSConfig:
    """TLS configuration class

    Args:
        ca_certs:
            a string path to the Certificate Authority certificate files that
            are to be treated as trusted by this client. If this is the only
            option given then the client will operate in a similar manner to
            a web browser. That is to say it will require the broker to have
            a certificate signed by the Certificate Authorities in ca_certs
            and will communicate using TLS v1.2, but will not attempt any
            form of authentication. This provides basic network encryption
            but may not be sufficient depending on how the broker is
            configured.
        certfile:
            string pointing to the PEM encoded client certificate. If this
            argument is not None then it will be used as client
            information for TLS based authentication. Support for this
            feature is broker dependent. Note that if this file is
            encrypted and needs a password to decrypt it, Python will ask
            for the password at the command line. It is not currently possible
            to define a callback to provide the password.
        keyfile:
            string pointing to the PEM encoded private keys. If this
            argument is not None then it will be used as client
            information for TLS based authentication. Support for this
            feature is broker dependent. Note that if this file is
            encrypted and needs a password to decrypt it, Python will ask
            for the password at the command line. It is not currently possible
            to define a callback to provide the password.
        cert_reqs:
            defines the certificate requirements that the client imposes on the
            broker. By default this is `ssl.CERT_REQUIRED`, which means that
            the broker must provide a certificate. See the ssl pydoc for more
            information on this parameter.
        tls_version:
            specifies the version of the SSL/TLS protocol to be used. By default
            (if the python version supports it) the highest TLS version is
            detected. If unavailable, TLS v1.2 is used. Previous versions
            (all versions beginning with SSL) are possible but not recommended
            due to possible security problems.
        ciphers:
            a string specifying which encryption ciphers are allowable for this
            connection, or `None` to use the defaults. See the ssl pydoc for more
            information.

    Returns:
        a TLSConfig object
    """

    ca_certs: Optional[str] = None
    certfile: Optional[str] = None
    keyfile: Optional[str] = None
    cert_reqs: ssl.VerifyMode = ssl.VerifyMode.CERT_REQUIRED
    tls_version: ssl._SSLMethod = ssl.PROTOCOL_TLS
    ciphers: Optional[str] = None


@dataclasses.dataclass(frozen=True)
class WSConfig:
    """Websockets configuration class

    Args:
        path:
            the mqtt path to use on the broker.
        headers:
            either a dictionary specifying a list of extra headers which should
            be appended to the standard websocket headers, or a callable that
            takes the normal websocket headers and returns a new dictionary
            with a set of headers to connect to the broker.

    Returns:
        a WSConfig object
    """

    path: str = "/mqtt"
    headers: Optional[
        Union[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]
    ] = None


@dataclasses.dataclass(frozen=True)
class ClientOptions:
    """Class of optional settings for an MQTT client

    Args:
        max_inflight_messages:
            maximum number of messages with QoS>0 that can be part way through
            their network flow at once. Increasing this value will consume
            more memory but can increase throughput.
        max_queued_messages:
            maximum number of outgoing messages with QoS>0 that can be pending
            in the outgoing message queue. 0 means unlimited, but due to
            implementation currently limited to 65555 (65535 messages in queue
            + 20 in flight). When the queue is full, any further outgoing
            messages would be dropped.
        message_retry_timeout:
            time in seconds before a message with QoS>0 is retried, if the
            broker does not respond. This is set to 5 seconds by default and
            should not normally need changing.
        reconnection_delay_min:
            when the connection is lost, the client will automatically retry
            connection. Initially, the attempt is delayed of min_delay seconds.
            It's doubled between subsequent attempts up to reconnection_delay_max.
        reconnection_delay_max:
            see `reconnection_delay_min`.
        reconnect_on_failure:
            whether or not to reconnect the client on failure

    Returns:
        a ClientOptions object
    """

    max_inflight_messages: int = 20
    max_queued_messages: int = 0
    message_retry_timeout: int = 5
    reconnection_delay_min: int = 1
    reconnection_delay_max: int = 120
    reconnect_on_failure: bool = True

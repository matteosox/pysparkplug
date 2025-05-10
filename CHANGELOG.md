# Changelog

All notable changes for `pysparkplug` will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## 0.6.1 (2025-05-10)

### Fixed
- Resolved `Client`'s `_on_connect` method, which iterated through its `_subscriptions` dict, which could be edited by another thread calling its `un/subscribe` method. See [Issue #20](https://github.com/matteosox/pysparkplug/issues/20).

## 0.6.0 (2025-02-16)

### Added
- Support for `MetaData` attribute of `Metric`'s, enabling multi-part uploads of bytes arrays or file types.

## 0.5.0 (2025-01-09)

### Added
- Support for array datatypes, i.e. INT8_ARRAY, INT16_ARRAY, INT32_ARRAY, INT64_ARRAY,
UINT8_ARRAY, UINT16_ARRAY, UINT32_ARRAY, UINT64_ARRAY, FLOAT_ARRAY, DOUBLE_ARRAY,
STRING_ARRAY, BOOLEAN_ARRAY, and DATETIME_ARRAY.

### Changed
- Payload `metrics` attribute is now type annotated and implemented as a `tuple`.
- `DATETIME` datatypes are no longer all treated as UTC, instead properly converting
them to the UTC timezone. Naive datetime objects are thus treated as the local
timezone.
- Unsupported datatypes now raise a `NotImplementedError` when attempting to encode/decode them instead of a `ValueError`.

## 0.4.0 (2024-10-24)

### Added
- Pysparkplug now supports Python 3.13

### Fixed
- `EdgeNode.disconnect` now correctly sends an NDEATH payload.

### Deprecated
- Pysparkplug no longer supports Python 3.8, which has reached its end of life.

## 0.3.2 (2024-05-06)

### Fixed
- Fixed topic for DDATA payloads resulting from the `EdgeNode.update_device` method.

## 0.3.1 (2024-02-13)

### Changed
- Pysparkplug is not compatible with the new 2.0 releasee of Paho, the underlying Python MQTT client.

## 0.3.0 (2024-01-13)

### Added
- Pysparkplug now supports Python 3.12

### Deprecated
- Pysparkplug no longer supports Python 3.7, which has reached its end of life.

## 0.2.0 (2023-08-23)

### Added
- `SINGLE_LEVEL_WILDCARD` and `MULTI_LEVEL_WILDCARD` wildcards for subscribing to multiple MQTT topics, conveniently typed to pass type checking

### Changed
- Refactored how dependencies are entered into the package's metadata, using `hatch-requirements-txt` referencing `requirements/requirements.txt`

### Removed
- Removed `Topic.to_string()`, since users should just use `str(topic)`.

### Fixed
- Explicitly making `MetricValue` available from the top-level package, resolving any type annotation issues.
- Fixed bug with implementation of `StrEnum` that resulted in enums not converting correctly to string. This resulted in topics not rendering to string correctly, since the `message_type` attribute was `MessageType`, an instance of `StrEnum`.
- Fixed bug with topic component validation, which was using the wrong wildcard constants `"#*"` instead of the correct `"#+"`.

## 0.1.0 (2023-08-13)

### Added
- `Client` low-level MQTT client
- `ClientOptions` class of optional settings for an MQTT client
- `ConnackCode` MQTT Connection Acknowledgement codes
- `DBirth` class representing a DBirth payload
- `DCmd` class representing a DCmd payload
- `DData` class representing a DData payload
- `DDeath` class representing a DDeath payload
- `DataType` enumeration of Sparkplug B datatypes
- `Device` class representing a Device in Sparkplug B
- `EdgeNode` class representing an EdgeNode in Sparkplug B
- `ErrorCode` MQTT error codes
- `MQTTError` Error from MQTT client
- `MQTTProtocol` MQTT protocol enum
- `Message` class representing a Sparkplug B message
- `MessageType` Sparkplug B message type enum
- `Metric` class representing a Sparkplug B metric
- `MetricValue` type alias for the Python type of the value of a Sparkplug B metric
- `NBirth` class representing a NBirth payload
- `NCmd` class representing a NCmd payload
- `NData` class representing a NData payload
- `NDeath` class representing a NDeath payload
- `QoS` MQTT quality of service enum
- `State` class representing a State payload
- `TLSConfig` TLS configuration class
- `Topic` class representing a Sparkplug B topic
- `Transport` MQTT transort enum
- `WSConfig` Websockets configuration class
- `get_current_timestamp` returns current time in a Sparkplug B compliant format

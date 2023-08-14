# Changelog

All notable changes for `pysparkplug` will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## Unreleased

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

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

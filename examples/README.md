# Pysparkplug Examples

This directory contains example scripts demonstrating how to use the Pysparkplug library. Each example is designed to showcase different aspects of the Sparkplug B protocol and library features.

## Prerequisites

- Python 3.8 or higher
- MQTT broker (e.g., Eclipse Mosquitto) running on localhost or accessible network
- Pysparkplug library installed: `pip install pysparkplug`

## Examples

### Basic Types (`basic_types.py`)

Demonstrates all Sparkplug B data types with edge cases and validation:

- Integer types (8-64 bits)
  - Signed: INT8, INT16, INT32, INT64
  - Unsigned: UINT8, UINT16, UINT32, UINT64
  - Edge cases: MIN/MAX values for each type
- Floating point: FLOAT, DOUBLE
  - Mathematical constants (π, e)
  - Edge cases (smallest/largest normalized)
- String types
  - ASCII and Unicode support
  - Emoji and special characters
- Other types
  - Boolean: True/False
  - DateTime: epoch, current, future dates
  - UUID and binary data

### Array Types (`array_types.py`)

Shows how to work with Sparkplug B array types:

- Integer arrays (signed/unsigned)
  - Full range testing (-MAX to +MAX)
  - Sequential and sparse values
- Float/Double arrays
  - Mathematical constants
  - Edge cases and special values
- String arrays
  - Mixed character sets
  - Unicode and emoji support
- DateTime arrays
  - Historical timestamps
  - Future dates
  - Timezone handling

### MQTT Monitor (`mqtt_monitor.py`)

Real-time monitoring tool for Sparkplug B messages with filtering capabilities:

```bash
# Show all Sparkplug B messages
python mqtt_monitor.py

# Filter by specific attributes
python mqtt_monitor.py --group my_group
python mqtt_monitor.py --node edge1 --device dev1
python mqtt_monitor.py --type DBIRTH

# Connect to remote broker
python mqtt_monitor.py --host broker.example.com --port 1883
```

Options:
- `--host`: MQTT broker hostname (default: localhost)
- `--port`: MQTT broker port (default: 1883)
- `--group`: Filter by group ID
- `--node`: Filter by edge node ID
- `--device`: Filter by device ID
- `--type`: Filter by message type (e.g., NBIRTH, DBIRTH, DDATA)

## Running the Examples

1. Ensure MQTT broker is running:
   ```bash
   # Start Mosquitto (if installed locally)
   mosquitto
   ```

2. Run desired example:
   ```bash
   python basic_types.py
   python array_types.py
   python mqtt_monitor.py
   ```

## Notes

- All examples include detailed comments explaining the code
- Timestamps are in UTC
- Examples demonstrate proper error handling
- Monitor tool supports real-time debugging
- Each example validates data before publishing

## Troubleshooting

1. Connection refused:
   - Verify MQTT broker is running
   - Check host/port settings
   - Ensure broker allows anonymous connections

2. Message not appearing:
   - Check topic filters
   - Verify message type matches filter
   - Ensure QoS settings match broker config
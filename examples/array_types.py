#!/usr/bin/env python3

from datetime import datetime, timezone

import pysparkplug as psp


def main():
    # Initialize client
    client = psp.Client()

    # Connect to MQTT broker
    host = "localhost"  # Change this to your MQTT broker address
    try:
        client.connect(host)
        print(f"Connected to MQTT broker at {host}")
    except ConnectionError as e:
        print(f"Failed to connect to MQTT broker at {host}: {e}")
        return

    try:
        # Define topic components
        group_id = "array_cases"
        edge_node_id = "array_node"
        device_id = "array_device"

        # Create metrics with different array types and edge cases
        metrics = [
            # Integer arrays with min/max values
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int8_array",
                datatype=psp.DataType.INT8_ARRAY,
                value=[-128, -64, 0, 63, 127],  # Full INT8 range
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int16_array",
                datatype=psp.DataType.INT16_ARRAY,
                value=[-32768, -16384, 0, 16383, 32767],  # Full INT16 range
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int32_array",
                datatype=psp.DataType.INT32_ARRAY,
                value=[
                    -2147483648,
                    -1073741824,
                    0,
                    1073741823,
                    2147483647,
                ],  # Full INT32 range
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int64_array",
                datatype=psp.DataType.INT64_ARRAY,
                value=[
                    -9223372036854775808,  # MIN
                    -4611686018427387904,  # MIN/2
                    0,
                    4611686018427387903,  # MAX/2
                    9223372036854775807,  # MAX
                ],
            ),
            # Unsigned integer arrays
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint8_array",
                datatype=psp.DataType.UINT8_ARRAY,
                value=[0, 63, 127, 191, 255],  # Full UINT8 range
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint16_array",
                datatype=psp.DataType.UINT16_ARRAY,
                value=[0, 16383, 32767, 49151, 65535],  # Full UINT16 range
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint32_array",
                datatype=psp.DataType.UINT32_ARRAY,
                value=[
                    0,
                    1073741823,
                    2147483647,
                    3221225471,
                    4294967295,
                ],  # Full UINT32 range
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint64_array",
                datatype=psp.DataType.UINT64_ARRAY,
                value=[
                    0,
                    4611686018427387903,  # MAX_INT64/2
                    9223372036854775807,  # MAX_INT64
                    13835058055282163711,  # 3*MAX_INT64/4
                    18446744073709551615,  # MAX_UINT64
                ],
            ),
            # Floating point arrays with special values
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="float_array",
                datatype=psp.DataType.FLOAT_ARRAY,
                value=[
                    1.175494e-38,  # Smallest normalized
                    3.14159265359,  # π
                    2.71828182846,  # e
                    1.41421356237,  # √2
                    3.402823e38,  # Largest normalized
                ],
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="double_array",
                datatype=psp.DataType.DOUBLE_ARRAY,
                value=[
                    2.2250738585072014e-308,  # Smallest normalized
                    3.141592653589793238,  # π (full precision)
                    2.718281828459045235,  # e (full precision)
                    1.414213562373095049,  # √2 (full precision)
                    1.7976931348623157e308,  # Largest normalized
                ],
            ),
            # Boolean array with alternating values
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="boolean_array",
                datatype=psp.DataType.BOOLEAN_ARRAY,
                value=[True, False, True, False, True],
            ),
            # String array with various types of strings
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="string_array",
                datatype=psp.DataType.STRING_ARRAY,
                value=[
                    "ASCII string",
                    "Unicode: 你好",
                    "Emoji: 🌍🚀",
                    "Special chars: \t\n\r",
                    "Mixed: Hello 世界 🌟",
                ],
            ),
            # DateTime array with special timestamps
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="datetime_array",
                datatype=psp.DataType.DATETIME_ARRAY,
                value=[
                    datetime(1970, 1, 1, tzinfo=timezone.utc),  # Unix epoch
                    datetime(2000, 1, 1, tzinfo=timezone.utc),  # Y2K
                    datetime.now(timezone.utc),  # Current time
                    datetime(2038, 1, 19, tzinfo=timezone.utc),  # Unix 32-bit limit
                    datetime(9999, 12, 31, tzinfo=timezone.utc),  # Far future
                ],
            ),
        ]

        # Create DBIRTH payload with metrics
        payload = psp.DBirth(
            timestamp=psp.get_current_timestamp(), metrics=metrics, seq=0
        )

        # Create topic for DBIRTH message
        topic = psp.Topic(
            message_type=psp.MessageType.DBIRTH,
            group_id=group_id,
            edge_node_id=edge_node_id,
            device_id=device_id,
        )

        print(f"Publishing DBIRTH message to topic: {topic}")
        # Publish the message
        client.publish(
            psp.Message(
                topic=topic, payload=payload, qos=psp.QoS.AT_LEAST_ONCE, retain=False
            ),
            include_dtypes=True,
        )
        print("Message published successfully!")

    finally:
        client.disconnect()
        print("Disconnected from MQTT broker")


if __name__ == "__main__":
    main()

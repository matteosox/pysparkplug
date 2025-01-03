#!/usr/bin/env python3

import uuid
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
        group_id = "edge_cases"
        edge_node_id = "all_types_node"
        device_id = "all_types_device"

        # Create metrics with edge case values
        metrics = [
            # Signed integers at their limits
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int8_min",
                datatype=psp.DataType.INT8,
                value=-128,  # -2^7
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int8_max",
                datatype=psp.DataType.INT8,
                value=127,  # 2^7 - 1
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int16_min",
                datatype=psp.DataType.INT16,
                value=-32768,  # -2^15
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int16_max",
                datatype=psp.DataType.INT16,
                value=32767,  # 2^15 - 1
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int32_min",
                datatype=psp.DataType.INT32,
                value=-2147483648,  # -2^31
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int32_max",
                datatype=psp.DataType.INT32,
                value=2147483647,  # 2^31 - 1
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int64_min",
                datatype=psp.DataType.INT64,
                value=-9223372036854775808,  # -2^63
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int64_max",
                datatype=psp.DataType.INT64,
                value=9223372036854775807,  # 2^63 - 1
            ),
            # Unsigned integers at their limits
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint8_min",
                datatype=psp.DataType.UINT8,
                value=0,
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint8_max",
                datatype=psp.DataType.UINT8,
                value=255,  # 2^8 - 1
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint16_min",
                datatype=psp.DataType.UINT16,
                value=0,
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint16_max",
                datatype=psp.DataType.UINT16,
                value=65535,  # 2^16 - 1
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint32_min",
                datatype=psp.DataType.UINT32,
                value=0,
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint32_max",
                datatype=psp.DataType.UINT32,
                value=4294967295,  # 2^32 - 1
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint64_min",
                datatype=psp.DataType.UINT64,
                value=0,
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uint64_max",
                datatype=psp.DataType.UINT64,
                value=18446744073709551615,  # 2^64 - 1
            ),
            # Floating point numbers
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="float_pi",
                datatype=psp.DataType.FLOAT,
                value=3.14159265359,  # Will be truncated to float precision
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="float_small",
                datatype=psp.DataType.FLOAT,
                value=1.175494e-38,  # Approximately smallest normalized float
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="float_big",
                datatype=psp.DataType.FLOAT,
                value=3.402823e38,  # Approximately largest float
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="double_pi",
                datatype=psp.DataType.DOUBLE,
                value=3.141592653589793238,  # Full double precision
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="double_small",
                datatype=psp.DataType.DOUBLE,
                value=2.2250738585072014e-308,  # Approximately smallest normalized double
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="double_big",
                datatype=psp.DataType.DOUBLE,
                value=1.7976931348623157e308,  # Approximately largest double
            ),
            # Boolean values
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="boolean_true",
                datatype=psp.DataType.BOOLEAN,
                value=True,
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="boolean_false",
                datatype=psp.DataType.BOOLEAN,
                value=False,
            ),
            # String types
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="string_ascii",
                datatype=psp.DataType.STRING,
                value="Hello, Sparkplug B!",
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="string_unicode",
                datatype=psp.DataType.STRING,
                value="Hello, 世界! 🌍",  # Unicode with emoji
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="text_multiline",
                datatype=psp.DataType.TEXT,
                value="Line 1\nLine 2\nLine 3",
            ),
            # Date and time
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="datetime_now",
                datatype=psp.DataType.DATETIME,
                value=datetime.now(timezone.utc),
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="datetime_epoch",
                datatype=psp.DataType.DATETIME,
                value=datetime(1970, 1, 1, tzinfo=timezone.utc),
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="datetime_future",
                datatype=psp.DataType.DATETIME,
                value=datetime(
                    2038, 1, 19, tzinfo=timezone.utc
                ),  # Near Unix 32-bit limit
            ),
            # UUID and bytes
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="uuid_random",
                datatype=psp.DataType.UUID,
                value=str(uuid.uuid4()),
            ),
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="bytes_data",
                datatype=psp.DataType.BYTES,
                value=b"Binary\x00Data\xff",
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
if __name__ == "__main__":
    main()

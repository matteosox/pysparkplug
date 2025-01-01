#!/usr/bin/env python3

import pysparkplug as psp
from datetime import datetime, timezone
import time

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
        group_id = "array_demo"
        edge_node_id = "array_node"

        # Create metrics with different array types
        metrics = [
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="int32_array",
                datatype=psp.DataType.INT32_ARRAY,
                value=[1, 2, 3, 4, 5]
            ),
            
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="float_array",
                datatype=psp.DataType.FLOAT_ARRAY,
                value=[1.1, 2.2, 3.3, 4.4, 5.5]
            ),
            
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="boolean_array",
                datatype=psp.DataType.BOOLEAN_ARRAY,
                value=[True, False, True, True, False]
            ),
            
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="string_array",
                datatype=psp.DataType.STRING_ARRAY,
                value=["one", "two", "three", "four", "five"]
            ),
            
            psp.Metric(
                timestamp=psp.get_current_timestamp(),
                name="datetime_array",
                datatype=psp.DataType.DATETIME_ARRAY,
                value=[
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ]
            )
        ]

        # Create NBIRTH payload with array metrics
        payload = psp.NBirth(
            timestamp=psp.get_current_timestamp(),
            metrics=metrics,
            seq=0
        )

        # Create topic for NBIRTH message
        topic = psp.Topic(
            message_type=psp.MessageType.NBIRTH,
            group_id=group_id,
            edge_node_id=edge_node_id
        )

        print(f"Publishing NBIRTH message to topic: {topic}")
        # Publish the message
        client.publish(
            psp.Message(
                topic=topic,
                payload=payload,
                qos=psp.QoS.AT_LEAST_ONCE,
                retain=False
            ),
            include_dtypes=True
        )
        print("Message published successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        # Clean up
        client.disconnect()
        print("Disconnected from MQTT broker")

if __name__ == "__main__":
    main()
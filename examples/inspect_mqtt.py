#!/usr/bin/env python3

import time

import pysparkplug as psp


def on_message(client, userdata, message):
    """Callback for when a message is received"""
    try:
        # Parse the Sparkplug B topic
        topic = psp.Topic.from_str(message.topic)

        # Skip STATE messages as they're handled differently
        if topic.message_type == psp.MessageType.STATE:
            print(f"\nReceived STATE message on topic: {topic}")
            return

        # Decode the payload based on the message type
        payload = topic.message_type.payload.decode(message.payload)

        print("\nReceived message:")
        print(f"Topic: {topic}")
        print(f"Message Type: {topic.message_type}")
        if hasattr(payload, "metrics"):
            print("Metrics:")
            for metric in payload.metrics:
                print(f"  {metric}")
        print("-------------------")
    except Exception as e:
        print(f"Error processing message on topic {message.topic}: {e}")


def main():
    # Initialize client
    client = psp.Client()

    # Connect to MQTT broker
    host = "localhost"
    try:
        client.connect(host)
        print(f"Connected to MQTT broker at {host}")
    except ConnectionError as e:
        print(f"Failed to connect to MQTT broker at {host}: {e}")
        return

    try:
        # Set message callback
        client._client.on_message = on_message

        # Subscribe to all Sparkplug B messages
        topic = "spBv1.0/#"  # Correct Sparkplug B wildcard topic
        client._client.subscribe(topic)
        print(f"Subscribed to topic: {topic}")

        # Keep script running
        print("Waiting for messages... (Press Ctrl+C to exit)")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        client.disconnect()
        print("Disconnected from MQTT broker")


if __name__ == "__main__":
    main()

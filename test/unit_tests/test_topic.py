"""Test suite for version information"""

import unittest

import pysparkplug as psp

GROUP_ID = "my_group_id"
EDGE_NODE_ID = "my_edge_node_id"
DEVICE_ID = "my_device_id"
SPARKPLUG_HOST_ID = "my_sparkplug_host_id"
INVALID_TOPIC_ID = r"+/sfddd#"


class TestTopic(unittest.TestCase):
    """Test suite for the topic object"""

    def test_ncmd(self) -> None:
        """Test a NCMD topic"""
        message_type = psp.MessageType.NCMD
        topic = psp.Topic(
            group_id=GROUP_ID, message_type=message_type, edge_node_id=EDGE_NODE_ID
        )
        self.assertEqual(
            str(topic),
            f"{psp.Topic.namespace}/{GROUP_ID}/{message_type}/{EDGE_NODE_ID}",
        )

    def test_dcmd(self) -> None:
        """Test a DCMD topic"""
        message_type = psp.MessageType.DCMD
        topic = psp.Topic(
            group_id=GROUP_ID,
            message_type=message_type,
            edge_node_id=EDGE_NODE_ID,
            device_id=DEVICE_ID,
        )
        self.assertEqual(
            str(topic),
            f"{psp.Topic.namespace}/{GROUP_ID}/{message_type}/{EDGE_NODE_ID}/{DEVICE_ID}",
        )

    def test_dcmd_with_wildcard(self) -> None:
        """Test a wildcard DCMD topic"""
        message_type = psp.MessageType.DCMD
        device_id = psp.SINGLE_LEVEL_WILDCARD
        topic = psp.Topic(
            group_id=GROUP_ID,
            message_type=message_type,
            edge_node_id=EDGE_NODE_ID,
            device_id=device_id,
        )
        self.assertEqual(
            str(topic),
            f"{psp.Topic.namespace}/{GROUP_ID}/{message_type}/{EDGE_NODE_ID}/{device_id}",
        )

    def test_complete_wildcard(self) -> None:
        """Test a full wildcard topic"""
        group_id = psp.MULTI_LEVEL_WILDCARD
        topic = psp.Topic(group_id=group_id)
        self.assertEqual(
            str(topic),
            f"{psp.Topic.namespace}/{group_id}",
        )

    def test_state_topic(self) -> None:
        """Test a state topic"""
        message_type = psp.MessageType.STATE
        topic = psp.Topic(
            sparkplug_host_id=SPARKPLUG_HOST_ID, message_type=message_type
        )
        self.assertEqual(
            str(topic),
            f"{psp.Topic.namespace}/{message_type}/{SPARKPLUG_HOST_ID}",
        )

    def test_state_wildcard_topic(self) -> None:
        """Test a state topic"""
        message_type = psp.MessageType.STATE
        sparkplug_host_id = psp.MULTI_LEVEL_WILDCARD
        topic = psp.Topic(
            sparkplug_host_id=sparkplug_host_id, message_type=message_type
        )
        self.assertEqual(
            str(topic),
            f"{psp.Topic.namespace}/{message_type}/{sparkplug_host_id}",
        )

    def test_message_type_wildcard(self) -> None:
        """Test a topic where the message_type is a wildcard"""
        message_type = psp.SINGLE_LEVEL_WILDCARD
        topic = psp.Topic(
            group_id=GROUP_ID,
            message_type=message_type,
            edge_node_id=EDGE_NODE_ID,
            device_id=DEVICE_ID,
        )
        self.assertEqual(
            str(topic),
            f"{psp.Topic.namespace}/{GROUP_ID}/{message_type}/{EDGE_NODE_ID}/{DEVICE_ID}",
        )

    def test_invalid_group_id(self) -> None:
        """Test that an invalid group_id raises an exception"""
        with self.assertRaisesRegex(ValueError, r"group_id"):
            psp.Topic(group_id=INVALID_TOPIC_ID)

    def test_invalid_device_id(self) -> None:
        """Test that an invalid device_id raises an exception"""
        with self.assertRaisesRegex(ValueError, r"device_id"):
            psp.Topic(
                group_id=GROUP_ID,
                message_type=psp.MessageType.NBIRTH,
                edge_node_id=EDGE_NODE_ID,
                device_id=INVALID_TOPIC_ID,
            )

    def test_invalid_edge_node_id(self) -> None:
        """Test that an invalid edge_node_id raises an exception"""
        with self.assertRaisesRegex(ValueError, r"edge_node_id"):
            psp.Topic(
                group_id=GROUP_ID,
                message_type=psp.MessageType.NBIRTH,
                edge_node_id=INVALID_TOPIC_ID,
            )

    def test_invalid_message_type(self) -> None:
        """Test that an invalid message_type raises an exception"""
        with self.assertRaisesRegex(ValueError, r"message_type"):
            psp.Topic(
                group_id=GROUP_ID,
                message_type=INVALID_TOPIC_ID,  # type: ignore[arg-type]
                edge_node_id=EDGE_NODE_ID,
                device_id=DEVICE_ID,
            )

    def test_invalid_sparkplug_host_id(self) -> None:
        """Test that an invalid sparkplug_host_id raises an exception"""
        with self.assertRaisesRegex(ValueError, r"sparkplug_host_id"):
            psp.Topic(
                sparkplug_host_id=INVALID_TOPIC_ID, message_type=psp.MessageType.STATE
            )

    def test_invalid_namespace(self) -> None:
        """Test that an invalid sparkplug_host_id raises an exception"""
        with self.assertRaisesRegex(ValueError, r"namespace"):
            psp.Topic.from_str("notspBv1.0/#")

    def test_dcmd_str(self) -> None:
        """Test a DCMD topic de/serializes to/from strings correctly"""
        message_type = psp.MessageType.DCMD
        topic = psp.Topic(
            group_id=GROUP_ID,
            message_type=message_type,
            edge_node_id=EDGE_NODE_ID,
            device_id=DEVICE_ID,
        )
        self.assertEqual(
            psp.Topic.from_str(str(topic)),
            topic,
        )

    def test_dcmd_with_wildcard_str(self) -> None:
        """Test a wildcard DCMD topic de/serializes to/from strings correctly"""
        message_type = psp.MessageType.DCMD
        device_id = psp.SINGLE_LEVEL_WILDCARD
        topic = psp.Topic(
            group_id=GROUP_ID,
            message_type=message_type,
            edge_node_id=EDGE_NODE_ID,
            device_id=device_id,
        )
        self.assertEqual(
            psp.Topic.from_str(str(topic)),
            topic,
        )

    def test_complete_wildcard_str(self) -> None:
        """Test a full wildcard topic de/serializes to/from strings correctly"""
        group_id = psp.MULTI_LEVEL_WILDCARD
        topic = psp.Topic(group_id=group_id)
        self.assertEqual(
            psp.Topic.from_str(str(topic)),
            topic,
        )

    def test_state_topic_str(self) -> None:
        """Test a state topic de/serializes to/from strings correctly"""
        message_type = psp.MessageType.STATE
        topic = psp.Topic(
            sparkplug_host_id=SPARKPLUG_HOST_ID, message_type=message_type
        )
        self.assertEqual(
            psp.Topic.from_str(str(topic)),
            topic,
        )

    def test_state_wildcard_topic_str(self) -> None:
        """Test a state topic de/serializes to/from strings correctly"""
        message_type = psp.MessageType.STATE
        sparkplug_host_id = psp.MULTI_LEVEL_WILDCARD
        topic = psp.Topic(
            sparkplug_host_id=sparkplug_host_id, message_type=message_type
        )
        self.assertEqual(
            psp.Topic.from_str(str(topic)),
            topic,
        )

    def test_message_type_wildcard_str(self) -> None:
        """Test a topic where the message_type is a wildcard de/serializes to/from strings correctly"""
        message_type = psp.SINGLE_LEVEL_WILDCARD
        topic = psp.Topic(
            group_id=GROUP_ID,
            message_type=message_type,
        )
        self.assertEqual(
            psp.Topic.from_str(str(topic)),
            topic,
        )

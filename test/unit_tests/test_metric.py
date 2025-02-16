"""Unit tests for Metric class"""

import unittest
from datetime import datetime, timezone

from pysparkplug import DataType, Metric, Metadata


class TestMetric(unittest.TestCase):
    """Test Metric functionality"""

    def test_basic_metric(self):
        """Test basic metric creation and conversion"""
        metric = Metric(
            timestamp=1234567890,
            name="test_metric",
            datatype=DataType.INT32,
            value=42,
        )

        # Convert to protobuf
        pb = metric.to_pb(include_dtype=True)
        self.assertEqual(pb.timestamp, 1234567890)
        self.assertEqual(pb.name, "test_metric")
        self.assertEqual(pb.int_value, 42)
        self.assertFalse(pb.is_null)

        # Convert back
        metric2 = Metric.from_pb(pb)
        self.assertEqual(metric2.timestamp, 1234567890)
        self.assertEqual(metric2.name, "test_metric")
        self.assertEqual(metric2.value, 42)
        self.assertFalse(metric2.is_null)

    def test_array_null_handling(self):
        """Test array handling with is_null flag"""
        test_cases = [
            # Empty array should be treated as null
            (None, True),
            # Non-empty array should not be null
            (("test",), False),
            # Array with empty string is not null
            (("",), False),
            # Multiple empty strings are not null
            (("", ""), False),
            # Mixed content is not null
            (("", "test", ""), False),
        ]

        for value, should_be_null in test_cases:
            with self.subTest(value=value, should_be_null=should_be_null):
                metric = Metric(
                    timestamp=1234567890,
                    name="test_array",
                    datatype=DataType.STRING_ARRAY,
                    value=value,
                )

                pb = metric.to_pb(include_dtype=True)
                self.assertEqual(pb.is_null, should_be_null)

                metric2 = Metric.from_pb(pb)
                self.assertEqual(metric2.is_null, should_be_null)
                if should_be_null:
                    self.assertIsNone(metric2.value)
                else:
                    self.assertEqual(metric2.value, value)

    def test_metric_properties(self):
        """Test metric property handling"""
        metric = Metric(
            timestamp=1234567890,
            name="test_metric",
            datatype=DataType.INT32,
            value=42,
            alias=123,
            is_historical=True,
            is_transient=True,
        )

        pb = metric.to_pb(include_dtype=True)
        self.assertEqual(pb.alias, 123)
        self.assertTrue(pb.is_historical)
        self.assertTrue(pb.is_transient)

        metric2 = Metric.from_pb(pb)
        self.assertEqual(metric2.alias, 123)
        self.assertTrue(metric2.is_historical)
        self.assertTrue(metric2.is_transient)

    def test_datetime_handling(self):
        """Test datetime value handling"""
        now = datetime.now(timezone.utc)
        metric = Metric(
            timestamp=int(now.timestamp()),  # Convert to milliseconds
            name="test_datetime",
            datatype=DataType.DATETIME,
            value=now,
        )

        pb = metric.to_pb(include_dtype=True)
        metric2 = Metric.from_pb(pb)
        self.assertEqual(metric2.timestamp, metric.timestamp)

    def test_metric_with_metadata(self):
        """Test metric creation with metadata and conversion"""
        metadata = Metadata(
            is_multipart=True,
            sequence_number=123,
        )
        metric = Metric(
            timestamp=1234567890,
            name="test_metric",
            datatype=DataType.INT32,
            value=42,
            metadata=metadata,
        )

        # Convert to protobuf
        pb = metric.to_pb(include_dtype=True)
        self.assertEqual(pb.timestamp, 1234567890)
        self.assertEqual(pb.name, "test_metric")
        self.assertEqual(pb.int_value, 42)
        self.assertFalse(pb.is_null)
        self.assertTrue(pb.metadata.is_multi_part)
        self.assertEqual(pb.metadata.seq, 123)

        # Convert back
        metric2 = Metric.from_pb(pb)
        self.assertEqual(metric2.timestamp, 1234567890)
        self.assertEqual(metric2.name, "test_metric")
        self.assertEqual(metric2.value, 42)
        self.assertFalse(metric2.is_null)
        self.assertIsNotNone(metric2.metadata)
        self.assertTrue(metric2.metadata.is_multipart)
        self.assertEqual(metric2.metadata.sequence_number, 123)

    def test_metric_with_null_metadata(self):
        """Test metric creation with null metadata and conversion"""
        metric = Metric(
            timestamp=1234567890,
            name="test_metric",
            datatype=DataType.INT32,
            value=42,
            metadata=None,
        )

        # Convert to protobuf
        pb = metric.to_pb(include_dtype=True)
        self.assertEqual(pb.timestamp, 1234567890)
        self.assertEqual(pb.name, "test_metric")
        self.assertEqual(pb.int_value, 42)
        self.assertFalse(pb.is_null)
        self.assertFalse(pb.HasField("metadata"))  # Ensure metadata is not set

        # Convert back
        metric2 = Metric.from_pb(pb)
        self.assertEqual(metric2.timestamp, 1234567890)
        self.assertEqual(metric2.name, "test_metric")
        self.assertEqual(metric2.value, 42)
        self.assertFalse(metric2.is_null)
        self.assertIsNone(metric2.metadata)  # Ensure metadata is None

    def test_metric_with_partial_metadata(self):
        """Test metric creation with partial metadata (only is_multipart)"""
        metadata = Metadata(
            is_multipart=True,
            sequence_number=None,
        )
        metric = Metric(
            timestamp=1234567890,
            name="test_metric",
            datatype=DataType.INT32,
            value=42,
            metadata=metadata,
        )

        # Convert to protobuf
        pb = metric.to_pb(include_dtype=True)
        self.assertEqual(pb.timestamp, 1234567890)
        self.assertEqual(pb.name, "test_metric")
        self.assertEqual(pb.int_value, 42)
        self.assertFalse(pb.is_null)
        self.assertTrue(pb.metadata.is_multi_part)
        self.assertFalse(pb.metadata.HasField("seq"))  # Ensure sequence_number is not set

        # Convert back
        metric2 = Metric.from_pb(pb)
        self.assertEqual(metric2.timestamp, 1234567890)
        self.assertEqual(metric2.name, "test_metric")
        self.assertEqual(metric2.value, 42)
        self.assertFalse(metric2.is_null)
        self.assertIsNotNone(metric2.metadata)
        self.assertTrue(metric2.metadata.is_multipart)
        self.assertIsNone(metric2.metadata.sequence_number)  # Ensure sequence_number is None

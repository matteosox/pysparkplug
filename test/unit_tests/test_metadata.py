import unittest
from pysparkplug._metadata import Metadata
from pysparkplug._protobuf import MetaData as PB_MetaData

class TestMetadata(unittest.TestCase):
    """Test Metadata functionality"""

    def test_metadata_full(self):
        """Test Metadata creation with all fields populated"""
        metadata = Metadata(
            is_multipart=True,
            sequence_number=123,
        )

        # Convert to protobuf
        pb = metadata.to_pb()
        self.assertTrue(pb.is_multi_part)
        self.assertEqual(pb.seq, 123)

        # Convert back
        metadata2 = Metadata.from_pb(pb)
        self.assertTrue(metadata2.is_multipart)
        self.assertEqual(metadata2.sequence_number, 123)

    def test_metadata_partial_is_multipart(self):
        """Test Metadata creation with only is_multipart populated"""
        metadata = Metadata(
            is_multipart=True,
            sequence_number=None,
        )

        # Convert to protobuf
        pb = metadata.to_pb()
        self.assertTrue(pb.is_multi_part)
        self.assertFalse(pb.HasField("seq"))  # Ensure sequence_number is not set

        # Convert back
        metadata2 = Metadata.from_pb(pb)
        self.assertTrue(metadata2.is_multipart)
        self.assertIsNone(metadata2.sequence_number)

    def test_metadata_partial_sequence_number(self):
        """Test Metadata creation with only sequence_number populated"""
        metadata = Metadata(
            is_multipart=None,
            sequence_number=456,
        )

        # Convert to protobuf
        pb = metadata.to_pb()
        self.assertFalse(pb.HasField("is_multi_part"))  # Ensure is_multipart is not set
        self.assertEqual(pb.seq, 456)

        # Convert back
        metadata2 = Metadata.from_pb(pb)
        self.assertIsNone(metadata2.is_multipart)
        self.assertEqual(metadata2.sequence_number, 456)

    def test_metadata_empty(self):
        """Test Metadata creation with no fields populated"""
        metadata = Metadata(
            is_multipart=None,
            sequence_number=None,
        )

        # Convert to protobuf
        pb = metadata.to_pb()
        self.assertFalse(pb.HasField("is_multi_part"))  # Ensure is_multipart is not set
        self.assertFalse(pb.HasField("seq"))  # Ensure sequence_number is not set

        # Convert back
        metadata2 = Metadata.from_pb(pb)
        self.assertIsNone(metadata2.is_multipart)
        self.assertIsNone(metadata2.sequence_number)

    def test_metadata_from_empty_pb(self):
        """Test Metadata creation from an empty Protobuf message"""
        pb = PB_MetaData()  # Create an empty Protobuf metadata message

        # Convert back
        metadata = Metadata.from_pb(pb)
        self.assertIsNone(metadata.is_multipart)
        self.assertIsNone(metadata.sequence_number)

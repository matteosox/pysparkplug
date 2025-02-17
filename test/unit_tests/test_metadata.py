import unittest

from pysparkplug._metadata import Metadata
from pysparkplug._protobuf import MetaData as PB_MetaData


class TestMetadata(unittest.TestCase):
    """Test Metadata functionality"""

    def test_metadata_full(self):
        """Test Metadata creation with all fields populated"""
        metadata = Metadata(
            is_multipart=True,
            content_type="json",
            size=256,
            seq=123,
            file_name="hello.json",
            file_type="json",
            md5="123456789abcdef",
            description="this is a description",
        )

        # Convert to protobuf
        pb = metadata.to_pb()
        self.assertTrue(pb.is_multi_part)
        self.assertEqual(pb.content_type, "json")
        self.assertEqual(pb.size, 256)
        self.assertEqual(pb.seq, 123)
        self.assertEqual(pb.file_name, "hello.json")
        self.assertEqual(pb.file_type, "json")
        self.assertEqual(pb.md5, "123456789abcdef")
        self.assertEqual(pb.description, "this is a description")

        # Convert back
        metadata2 = Metadata.from_pb(pb)
        self.assertTrue(metadata2.is_multipart)
        self.assertEqual(metadata2.content_type, "json")
        self.assertEqual(metadata2.size, 256)
        self.assertEqual(metadata2.seq, 123)
        self.assertEqual(metadata2.file_name, "hello.json")
        self.assertEqual(metadata2.file_type, "json")
        self.assertEqual(metadata2.md5, "123456789abcdef")
        self.assertEqual(metadata2.description, "this is a description")

    def test_metadata_partial_is_multipart(self):
        """Test Metadata creation with only is_multipart populated"""
        metadata = Metadata(
            is_multipart=True,
        )

        # Convert to protobuf
        pb = metadata.to_pb()
        self.assertTrue(pb.is_multi_part)
        self.assertFalse(pb.HasField("content_type"))
        self.assertFalse(pb.HasField("size"))
        self.assertFalse(pb.HasField("seq"))
        self.assertFalse(pb.HasField("file_name"))
        self.assertFalse(pb.HasField("file_type"))
        self.assertFalse(pb.HasField("md5"))
        self.assertFalse(pb.HasField("description"))

        # Convert back
        metadata2 = Metadata.from_pb(pb)
        self.assertTrue(metadata2.is_multipart)
        self.assertIsNone(metadata2.content_type)
        self.assertIsNone(metadata2.size)
        self.assertIsNone(metadata2.seq)
        self.assertIsNone(metadata2.file_name)
        self.assertIsNone(metadata2.file_type)
        self.assertIsNone(metadata2.md5)
        self.assertIsNone(metadata2.description)

    def test_metadata_partial_sequence_number(self):
        """Test Metadata creation with only sequence_number populated"""
        metadata = Metadata(
            seq=456,
        )

        # Convert to protobuf
        pb = metadata.to_pb()
        self.assertFalse(pb.HasField("is_multi_part"))  # Ensure is_multipart is not set
        self.assertFalse(pb.HasField("content_type"))
        self.assertFalse(pb.HasField("size"))
        self.assertEqual(pb.seq, 456)
        self.assertFalse(pb.HasField("file_name"))
        self.assertFalse(pb.HasField("file_type"))
        self.assertFalse(pb.HasField("md5"))
        self.assertFalse(pb.HasField("description"))

        # Convert back
        metadata2 = Metadata.from_pb(pb)
        self.assertIsNone(metadata2.is_multipart)
        self.assertIsNone(metadata2.content_type)
        self.assertIsNone(metadata2.size)
        self.assertEqual(metadata2.seq, 456)
        self.assertIsNone(metadata2.file_name)
        self.assertIsNone(metadata2.file_type)
        self.assertIsNone(metadata2.md5)
        self.assertIsNone(metadata2.description)

    def test_metadata_empty(self):
        """Test Metadata creation with no fields populated"""
        metadata = Metadata()

        # Convert to protobuf
        pb = metadata.to_pb()
        self.assertFalse(pb.HasField("is_multi_part"))  # Ensure is_multipart is not set
        self.assertFalse(pb.HasField("content_type"))
        self.assertFalse(pb.HasField("size"))
        self.assertFalse(pb.HasField("seq"))
        self.assertFalse(pb.HasField("file_name"))
        self.assertFalse(pb.HasField("file_type"))
        self.assertFalse(pb.HasField("md5"))
        self.assertFalse(pb.HasField("description"))

        # Convert back
        metadata2 = Metadata.from_pb(pb)
        self.assertIsNone(metadata2.is_multipart)
        self.assertIsNone(metadata2.content_type)
        self.assertIsNone(metadata2.size)
        self.assertIsNone(metadata2.seq)
        self.assertIsNone(metadata2.file_name)
        self.assertIsNone(metadata2.file_type)
        self.assertIsNone(metadata2.md5)
        self.assertIsNone(metadata2.description)

    def test_metadata_from_empty_pb(self):
        """Test Metadata creation from an empty Protobuf message"""
        pb = PB_MetaData()  # Create an empty Protobuf metadata message

        # Convert back
        metadata = Metadata.from_pb(pb)
        self.assertIsNone(metadata.is_multipart)
        self.assertIsNone(metadata.content_type)
        self.assertIsNone(metadata.size)
        self.assertIsNone(metadata.seq)
        self.assertIsNone(metadata.file_name)
        self.assertIsNone(metadata.file_type)
        self.assertIsNone(metadata.md5)
        self.assertIsNone(metadata.description)

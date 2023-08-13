"""Test suite for version information"""

import importlib.metadata
import unittest

import packaging.version

import pysparkplug as psp


class TestVersion(unittest.TestCase):
    """Test the package version is correct"""

    def test_version_metadata(self) -> None:
        """Confirm the pysparkplug package has a valid version in its metadata"""
        packaging.version.Version(importlib.metadata.version("pysparkplug"))

    def test_version(self) -> None:
        """Test the pysparkplug package has a valid version"""
        packaging.version.Version(psp.__version__)

    def test_version_match(self) -> None:
        """Test the pysparkplug package version matches its metadata"""
        self.assertEqual(psp.__version__, importlib.metadata.version("pysparkplug"))

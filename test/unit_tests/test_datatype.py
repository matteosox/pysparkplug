"""Unit tests for DataType functionality"""

import math
import unittest
from datetime import datetime, timedelta, timezone
from typing import List, cast

from pysparkplug import DataType


class TestIntegerTypes(unittest.TestCase):
    """Test integer type functionality"""

    def test_integer_encoding(self):
        """Test integer encoding/decoding with edge cases for all integer types"""
        test_cases = [
            # INT8 (-128 to 127)
            (DataType.INT8, -128, False),  # Min INT8
            (DataType.INT8, 127, False),  # Max INT8
            (DataType.INT8, -129, True),  # Below MIN - should raise
            (DataType.INT8, 128, True),  # Above MAX - should raise
            # UINT8 (0 to 255)
            (DataType.UINT8, 0, False),  # Min UINT8
            (DataType.UINT8, 255, False),  # Max UINT8
            (DataType.UINT8, -1, True),  # Below MIN - should raise
            (DataType.UINT8, 256, True),  # Above MAX - should raise
            # INT16 (-32768 to 32767)
            (DataType.INT16, -32768, False),  # Min INT16
            (DataType.INT16, 32767, False),  # Max INT16
            (DataType.INT16, -32769, True),  # Below MIN - should raise
            (DataType.INT16, 32768, True),  # Above MAX - should raise
            # UINT16 (0 to 65535)
            (DataType.UINT16, 0, False),  # Min UINT16
            (DataType.UINT16, 65535, False),  # Max UINT16
            (DataType.UINT16, -1, True),  # Below MIN - should raise
            (DataType.UINT16, 65536, True),  # Above MAX - should raise
            # INT32 (-2147483648 to 2147483647)
            (DataType.INT32, -2147483648, False),  # Min INT32
            (DataType.INT32, 2147483647, False),  # Max INT32
            (DataType.INT32, -2147483649, True),  # Below MIN - should raise
            (DataType.INT32, 2147483648, True),  # Above MAX - should raise
            # UINT32 (0 to 4294967295)
            (DataType.UINT32, 0, False),  # Min UINT32
            (DataType.UINT32, 4294967295, False),  # Max UINT32
            (DataType.UINT32, -1, True),  # Below MIN - should raise
            (DataType.UINT32, 4294967296, True),  # Above MAX - should raise
            # INT64 (-9223372036854775808 to 9223372036854775807)
            (DataType.INT64, -9223372036854775808, False),  # Min INT64
            (DataType.INT64, 9223372036854775807, False),  # Max INT64
            (DataType.INT64, -9223372036854775809, True),  # Below MIN - should raise
            (DataType.INT64, 9223372036854775808, True),  # Above MAX - should raise
            # UINT64 (0 to 18446744073709551615)
            (DataType.UINT64, 0, False),  # Min UINT64
            (DataType.UINT64, 18446744073709551615, False),  # Max UINT64
            (DataType.UINT64, -1, True),  # Below MIN - should raise
            (DataType.UINT64, 18446744073709551616, True),  # Above MAX - should raise
            # Additional edge cases
            (DataType.INT8, 0, False),  # Zero for signed
            (DataType.UINT8, 0, False),  # Zero for unsigned
            (DataType.INT64, 1, False),  # Small positive for large type
            (DataType.UINT64, 1, False),  # Small positive for large type
            (DataType.INT32, -1, False),  # Negative one
            (DataType.INT16, -1, False),  # Negative one in smaller type
        ]

        for dtype, value, should_raise in test_cases:
            with self.subTest(dtype=dtype, value=value):
                if should_raise:
                    with self.assertRaises(OverflowError):
                        dtype.encode(value)
                else:
                    encoded = dtype.encode(value)
                    decoded = dtype.decode(encoded)
                    self.assertEqual(
                        decoded, value, f"Failed to encode/decode {value} with {dtype}"
                    )

    def test_float_encoding(self):
        """Test floating point encoding/decoding with edge cases

        Tests both FLOAT (32-bit) and DOUBLE (64-bit) types, including:
        - Normal numbers
        - Denormalized numbers
        - Special values (inf, -inf, nan)
        - Edge cases (max/min values)
        - Zero and negative zero
        """
        test_cases = [
            # Normal numbers - FLOAT
            (DataType.FLOAT, 0.0),
            (DataType.FLOAT, 1.0),
            (DataType.FLOAT, -1.0),
            (DataType.FLOAT, 3.14159),
            (DataType.FLOAT, -3.14159),
            # Normal numbers - DOUBLE
            (DataType.DOUBLE, 0.0),
            (DataType.DOUBLE, 1.0),
            (DataType.DOUBLE, -1.0),
            (DataType.DOUBLE, math.pi),
            (DataType.DOUBLE, -math.pi),
            (DataType.DOUBLE, math.e),
            # Special values - FLOAT
            (DataType.FLOAT, float("inf")),
            (DataType.FLOAT, float("-inf")),
            (DataType.FLOAT, float("nan")),
            # Special values - DOUBLE
            (DataType.DOUBLE, float("inf")),
            (DataType.DOUBLE, float("-inf")),
            (DataType.DOUBLE, float("nan")),
            # Denormalized numbers - FLOAT
            (DataType.FLOAT, 1.4e-45),  # Smallest positive denormal float
            (DataType.FLOAT, -1.4e-45),  # Largest negative denormal float
            # Denormalized numbers - DOUBLE
            (DataType.DOUBLE, 4.9e-324),  # Smallest positive denormal double
            (DataType.DOUBLE, -4.9e-324),  # Largest negative denormal double
            # Edge cases - FLOAT
            (DataType.FLOAT, 3.4e38),  # Near max float
            (DataType.FLOAT, -3.4e38),  # Near min float
            (DataType.FLOAT, 1.2e-38),  # Near smallest normal float
            (DataType.FLOAT, -1.2e-38),  # Near largest normal negative float
            # Edge cases - DOUBLE
            (DataType.DOUBLE, 1.8e308),  # Near max double
            (DataType.DOUBLE, -1.8e308),  # Near min double
            (DataType.DOUBLE, 2.2e-308),  # Near smallest normal double
            (DataType.DOUBLE, -2.2e-308),  # Near largest normal negative double
            # Zero representations
            (DataType.FLOAT, 0.0),
            (DataType.FLOAT, -0.0),
            (DataType.DOUBLE, 0.0),
            (DataType.DOUBLE, -0.0),
            # Specific decimal values
            (DataType.FLOAT, 0.1),
            (DataType.FLOAT, 0.2),
            (DataType.DOUBLE, 0.1),
            (DataType.DOUBLE, 0.2),
            # Powers of 2
            (DataType.FLOAT, 2.0),
            (DataType.FLOAT, 4.0),
            (DataType.FLOAT, 8.0),
            (DataType.DOUBLE, 2.0),
            (DataType.DOUBLE, 4.0),
            (DataType.DOUBLE, 8.0),
        ]

        for dtype, value in test_cases:
            with self.subTest(dtype=dtype, value=value):
                encoded = dtype.encode(value)
                decoded = cast(float, dtype.decode(encoded))

                if math.isnan(value):
                    self.assertTrue(
                        math.isnan(decoded), f"Expected NaN, got {decoded} for {dtype}"
                    )
                elif math.isinf(value):
                    self.assertTrue(
                        math.isinf(decoded),
                        f"Expected {value}, got {decoded} for {dtype}",
                    )
                    # Check sign of infinity
                    self.assertEqual(
                        math.copysign(1, value),
                        math.copysign(1, decoded),
                        f"Infinity sign mismatch for {dtype}",
                    )
                else:
                    # For normal numbers, compare with relative tolerance
                    self.assertAlmostEqual(
                        decoded,
                        value,
                        places=6 if dtype == DataType.FLOAT else 15,
                        msg=f"Value mismatch for {dtype}: expected {value}, got {decoded}",
                    )
                    # Check sign of zero
                    if value == 0:
                        self.assertEqual(
                            math.copysign(1, value),
                            math.copysign(1, decoded),
                            f"Zero sign mismatch for {dtype}",
                        )

    def test_datetime_encoding(self):
        """Test datetime encoding/decoding with timezones"""
        test_cases = [
            # UTC timezone
            (datetime(2023, 1, 1, tzinfo=timezone.utc), 1672531200000),
            # Local timezone - using UTC for consistency
            (datetime.now(timezone.utc), None),  # Dynamic value
            # Specific timezone - converting to UTC for comparison
            (
                datetime(
                    2023, 1, 1, 12, 0, tzinfo=timezone(timedelta(hours=5))
                ).astimezone(timezone.utc),
                1672556400000,  # 2023-01-01 07:00:00 UTC
            ),
            # Edge cases
            (datetime(1970, 1, 1, tzinfo=timezone.utc), 0),  # Epoch
            (
                datetime(2038, 1, 19, 3, 14, 7, tzinfo=timezone.utc),
                2147483647000,
            ),  # 32-bit limit (2^31 - 1 seconds)
        ]

        for dt, expected in test_cases:
            with self.subTest(dt=dt):
                encoded = DataType.DATETIME.encode(dt)
                if expected is not None:
                    self.assertEqual(encoded, expected)
                decoded = cast(datetime, DataType.DATETIME.decode(encoded))
                # Compare timestamps in UTC, truncating microseconds
                decoded_ts = int(decoded.timestamp() * 1000) / 1000
                original_ts = int(dt.timestamp() * 1000) / 1000
                self.assertEqual(decoded_ts, original_ts)

    def test_string_encoding(self) -> None:
        """Test string encoding/decoding with comprehensive character sets and edge cases

        Tests:
        - Empty and basic strings
        - Unicode characters from different planes
        - Special characters
        - Length limits and boundary cases
        - Mixed content strings
        - Various newline combinations
        """
        test_cases = [
            # Empty and basic strings
            "",  # Empty string
            "Hello",  # Basic ASCII
            "Hello123",  # ASCII with numbers
            # Unicode characters
            "Hello 世界",  # Basic Unicode
            "こんにちは",  # Japanese
            "안녕하세요",  # Korean
            "Привет",  # Cyrillic
            "مرحبا",  # Arabic
            "שָׁלוֹם",  # Hebrew with diacritics
            # Emojis and symbols
            "Hello 👋 World 🌍",  # Basic emojis
            "❤️ 💔 💝 👨‍👩‍👧‍👦",  # Emojis with modifiers and ZWJ sequences
            "™ ® © ¥ £ € ¢ ₿",  # Special symbols
            # Control characters
            "Line1\nLine2",  # Newline
            "Column1\tColumn2",  # Tab
            "Text\rReturn",  # Carriage return
            "Mixed\r\nNewlines",  # CRLF
            "Bell\aBell",  # Bell
            "Back\bspace",  # Backspace
            "Form\ffeed",  # Form feed
            "Vertical\vtab",  # Vertical tab
            # Special characters
            'Quote"Quote',  # Double quote
            "Single'Quote",  # Single quote
            "Back\\slash",  # Backslash
            "Null\x00Char",  # Null character
            # Mixed content
            "ASCII-123 世界 👋 \n\t\r",  # Mix of different types
            "Mixed\x00With\x00Null",  # Multiple null characters
            "🌍\n世界\r안녕",  # Unicode with control chars
            # Length edge cases
            "x",  # Single character
            "x" * 100,  # Medium length
            "x" * 1000,  # Long string
            "a" * 65535,  # Maximum length (UINT16_MAX)
        ]

        for text in test_cases:
            with self.subTest(text=text[:50] + "..." if len(text) > 50 else text):
                try:
                    encoded = DataType.STRING.encode(text)
                    decoded = cast(str, DataType.STRING.decode(encoded))
                    self.assertEqual(decoded, text)

                    # Additional checks for specific cases
                    if isinstance(encoded, bytes):  # Type guard for encoded
                        # Check empty string encoding length
                        if not text:
                            self.assertEqual(len(encoded), 2)

                        # Verify null character handling
                        if "\x00" in text:
                            self.assertTrue(b"\x00" in encoded)

                        # Verify encoding length
                        text_bytes = text.encode("utf-8")
                        self.assertLessEqual(len(encoded), 2 + len(text_bytes))

                except Exception as e:
                    self.fail(
                        f"Failed to encode/decode string: {text[:50]}... Error: {e!s}"
                    )

        def test_string_length_limits(self: unittest.TestCase) -> None:
            """Test string length limits and boundary conditions"""
            # Test exactly at UINT16_MAX
            max_string = "x" * 65535
            encoded = DataType.STRING.encode(max_string)
            decoded = cast(str, DataType.STRING.decode(encoded))
            self.assertEqual(decoded, max_string)

            # Test exceeding UINT16_MAX
            with self.assertRaises(ValueError):
                DataType.STRING.encode("x" * 65536)

            # Test long Unicode strings
            long_unicode = "世界" * 32767  # Just under UINT16_MAX in UTF-8 bytes
            encoded = DataType.STRING.encode(long_unicode)
            decoded = cast(str, DataType.STRING.decode(encoded))
            self.assertEqual(decoded, long_unicode)

        def test_invalid_utf8_handling(self: unittest.TestCase) -> None:
            """Test handling of invalid UTF-8 sequences"""
            with self.assertRaises(UnicodeEncodeError):
                # Create an invalid UTF-8 sequence
                DataType.STRING.decode(b"\xff\xff")


class TestArrayTypes(unittest.TestCase):
    """Test array type functionality"""

    def test_integer_array_validation(self):
        """Test integer array validation with boundaries and overflow cases"""
        test_cases = [
            # INT8 (-128 to 127)
            (DataType.INT8_ARRAY, [-128], None),  # Min value
            (DataType.INT8_ARRAY, [127], None),  # Max value
            (DataType.INT8_ARRAY, [-128, -1, 0, 1, 127], None),  # Range of values
            (DataType.INT8_ARRAY, [-129], OverflowError),  # Below min
            (DataType.INT8_ARRAY, [128], OverflowError),  # Above max
            (DataType.INT8_ARRAY, [-128, 128], OverflowError),  # Valid and invalid
            # UINT8 (0 to 255)
            (DataType.UINT8_ARRAY, [0], None),  # Min value
            (DataType.UINT8_ARRAY, [255], None),  # Max value
            (DataType.UINT8_ARRAY, [0, 1, 128, 255], None),  # Range of values
            (DataType.UINT8_ARRAY, [-1], OverflowError),  # Below min
            (DataType.UINT8_ARRAY, [256], OverflowError),  # Above max
            (DataType.UINT8_ARRAY, [0, 256], OverflowError),  # Valid and invalid
            # INT16 (-32768 to 32767)
            (DataType.INT16_ARRAY, [-32768], None),  # Min value
            (DataType.INT16_ARRAY, [32767], None),  # Max value
            (DataType.INT16_ARRAY, [-32768, -1, 0, 1, 32767], None),  # Range of values
            (DataType.INT16_ARRAY, [-32769], OverflowError),  # Below min
            (DataType.INT16_ARRAY, [32768], OverflowError),  # Above max
            (DataType.INT16_ARRAY, [-32768, 32768], OverflowError),  # Valid and invalid
            # UINT16 (0 to 65535)
            (DataType.UINT16_ARRAY, [0], None),  # Min value
            (DataType.UINT16_ARRAY, [65535], None),  # Max value
            (DataType.UINT16_ARRAY, [0, 1, 32768, 65535], None),  # Range of values
            (DataType.UINT16_ARRAY, [-1], OverflowError),  # Below min
            (DataType.UINT16_ARRAY, [65536], OverflowError),  # Above max
            (DataType.UINT16_ARRAY, [0, 65536], OverflowError),  # Valid and invalid
            # INT32 (-2147483648 to 2147483647)
            (DataType.INT32_ARRAY, [-2147483648], None),  # Min value
            (DataType.INT32_ARRAY, [2147483647], None),  # Max value
            (
                DataType.INT32_ARRAY,
                [-2147483648, -1, 0, 1, 2147483647],
                None,
            ),  # Range of values
            (DataType.INT32_ARRAY, [-2147483649], OverflowError),  # Below min
            (DataType.INT32_ARRAY, [2147483648], OverflowError),  # Above max
            (
                DataType.INT32_ARRAY,
                [-2147483648, 2147483648],
                OverflowError,
            ),  # Valid and invalid
            # UINT32 (0 to 4294967295)
            (DataType.UINT32_ARRAY, [0], None),  # Min value
            (DataType.UINT32_ARRAY, [4294967295], None),  # Max value
            (
                DataType.UINT32_ARRAY,
                [0, 1, 2147483648, 4294967295],
                None,
            ),  # Range of values
            (DataType.UINT32_ARRAY, [-1], OverflowError),  # Below min
            (DataType.UINT32_ARRAY, [4294967296], OverflowError),  # Above max
            (
                DataType.UINT32_ARRAY,
                [0, 4294967296],
                OverflowError,
            ),  # Valid and invalid
            # INT64 (-9223372036854775808 to 9223372036854775807)
            (DataType.INT64_ARRAY, [-9223372036854775808], None),  # Min value
            (DataType.INT64_ARRAY, [9223372036854775807], None),  # Max value
            (
                DataType.INT64_ARRAY,
                [-9223372036854775808, -1, 0, 1, 9223372036854775807],
                None,
            ),  # Range
            (DataType.INT64_ARRAY, [-9223372036854775809], OverflowError),  # Below min
            (DataType.INT64_ARRAY, [9223372036854775808], OverflowError),  # Above max
            (
                DataType.INT64_ARRAY,
                [-9223372036854775808, 9223372036854775808],
                OverflowError,
            ),  # Valid and invalid
            # UINT64 (0 to 18446744073709551615)
            (DataType.UINT64_ARRAY, [0], None),  # Min value
            (DataType.UINT64_ARRAY, [18446744073709551615], None),  # Max value
            (
                DataType.UINT64_ARRAY,
                [0, 1, 9223372036854775808, 18446744073709551615],
                None,
            ),  # Range
            (DataType.UINT64_ARRAY, [-1], OverflowError),  # Below min
            (DataType.UINT64_ARRAY, [18446744073709551616], OverflowError),  # Above max
            (
                DataType.UINT64_ARRAY,
                [0, 18446744073709551616],
                OverflowError,
            ),  # Valid and invalid
        ]

        for dtype, value, expected_error in test_cases:
            with self.subTest(dtype=dtype, value=value):
                if expected_error is None:
                    encoded = dtype.encode(value)
                    decoded = dtype.decode(encoded)
                    self.assertEqual(decoded, value)
                else:
                    with self.assertRaises(expected_error):
                        dtype.encode(value)

    def test_float_array_validation(self):
        """Test floating point array validation"""
        test_cases = [
            # FLOAT basic cases
            (DataType.FLOAT_ARRAY, [0.0], None),  # Zero
            (DataType.FLOAT_ARRAY, [-1.0, 1.0], None),  # Unit values
            (DataType.FLOAT_ARRAY, [3.14159, -3.14159], None),  # Common pi
            # FLOAT boundary cases
            (DataType.FLOAT_ARRAY, [3.4028235e38], None),  # Max float32
            (DataType.FLOAT_ARRAY, [-3.4028235e38], None),  # Min float32
            (DataType.FLOAT_ARRAY, [1.17549435e-38], None),  # Min positive normal
            (DataType.FLOAT_ARRAY, [1.4e-45], None),  # Min positive subnormal
            # FLOAT special values
            (DataType.FLOAT_ARRAY, [float("inf")], None),
            (DataType.FLOAT_ARRAY, [float("-inf")], None),
            (DataType.FLOAT_ARRAY, [float("nan")], None),
            (DataType.FLOAT_ARRAY, [float("inf"), float("-inf"), float("nan")], None),
            # FLOAT mixed values
            (DataType.FLOAT_ARRAY, [1, 1.0, 1.5], None),  # Mixed integers and floats
            (DataType.FLOAT_ARRAY, [-3.4028235e38, 0.0, 3.4028235e38], None),  # Range
            # DOUBLE basic cases
            (DataType.DOUBLE_ARRAY, [0.0], None),  # Zero
            (DataType.DOUBLE_ARRAY, [-1.0, 1.0], None),  # Unit values
            (DataType.DOUBLE_ARRAY, [math.pi, -math.pi], None),  # Pi
            # DOUBLE boundary cases
            (DataType.DOUBLE_ARRAY, [1.7976931348623157e308], None),  # Max double
            (DataType.DOUBLE_ARRAY, [-1.7976931348623157e308], None),  # Min double
            (
                DataType.DOUBLE_ARRAY,
                [2.2250738585072014e-308],
                None,
            ),  # Min positive normal
            (
                DataType.DOUBLE_ARRAY,
                [4.9406564584124654e-324],
                None,
            ),  # Min positive subnormal
            # DOUBLE special values
            (DataType.DOUBLE_ARRAY, [float("inf")], None),
            (DataType.DOUBLE_ARRAY, [float("-inf")], None),
            (DataType.DOUBLE_ARRAY, [float("nan")], None),
            (DataType.DOUBLE_ARRAY, [float("inf"), float("-inf"), float("nan")], None),
            # DOUBLE mixed values
            (DataType.DOUBLE_ARRAY, [1, 1.0, 1.5], None),  # Mixed integers and floats
            (
                DataType.DOUBLE_ARRAY,
                [-1.7976931348623157e308, 0.0, 1.7976931348623157e308],
                None,
            ),  # Range
            # Testing precision
            (DataType.FLOAT_ARRAY, [1.23456789], None),  # Beyond float32 precision
            (
                DataType.DOUBLE_ARRAY,
                [1.234567890123456789],
                None,
            ),  # Beyond float64 precision
        ]

        for dtype, value, expected_error in test_cases:
            with self.subTest(dtype=dtype, value=value):
                encoded = dtype.encode(value)
                decoded = dtype.decode(encoded)
                self.assertEqual(len(decoded), len(value))
                for orig, dec in zip(value, decoded):
                    if math.isnan(orig) and math.isnan(dec):
                        continue

                    # Different handling based on value magnitude
                    if dtype == DataType.FLOAT_ARRAY:
                        rtol = 1e-6
                        atol = 1e-45  # For float32 subnormal values
                    else:
                        rtol = 1e-15
                        atol = 1e-308  # For float64 subnormal values

                    self.assertTrue(
                        math.isclose(dec, orig, rel_tol=rtol, abs_tol=atol),
                        msg=f"Failed comparing {orig} and {dec} for {dtype}. "
                        f"Relative difference: {abs(dec-orig)/abs(orig) if orig != 0 else abs(dec-orig)}",
                    )

    def test_integer_array_type_errors(self):
        """Test integer array validation with invalid type combinations"""
        test_cases = [
            # INT8 type mixing - within array
            (DataType.INT8_ARRAY, [-128, "string"], TypeError, "int8 with string"),
            (DataType.INT8_ARRAY, [127, 3.14], TypeError, "int8 with float"),
            (DataType.INT8_ARRAY, [0, None], TypeError, "int8 with None"),
            (DataType.INT8_ARRAY, [0, [1]], TypeError, "int8 with list"),
            (DataType.INT8_ARRAY, [0, {}], TypeError, "int8 with dict"),
            # UINT8 type mixing - within array
            (DataType.UINT8_ARRAY, [255, "abc"], TypeError, "uint8 with string"),
            (DataType.UINT8_ARRAY, [0, 1.5], TypeError, "uint8 with float"),
            (DataType.UINT8_ARRAY, [128, None], TypeError, "uint8 with None"),
            (DataType.UINT8_ARRAY, [0, (1,)], TypeError, "uint8 with tuple"),
            # INT16 type mixing - within array
            (DataType.INT16_ARRAY, [-32768, "xyz"], TypeError, "int16 with string"),
            (DataType.INT16_ARRAY, [32767, 2.718], TypeError, "int16 with float"),
            (DataType.INT16_ARRAY, [0, {}], TypeError, "int16 with dict"),
            (DataType.INT16_ARRAY, [0, set([1])], TypeError, "int16 with set"),
            # UINT16 type mixing - within array
            (DataType.UINT16_ARRAY, [65535, "test"], TypeError, "uint16 with string"),
            (DataType.UINT16_ARRAY, [0, 3.14159], TypeError, "uint16 with float"),
            (DataType.UINT16_ARRAY, [1, []], TypeError, "uint16 with empty list"),
            # INT32 type mixing - within array
            (
                DataType.INT32_ARRAY,
                [-2147483648, "large"],
                TypeError,
                "int32 with string",
            ),
            (
                DataType.INT32_ARRAY,
                [2147483647, 1.23e5],
                TypeError,
                "int32 with scientific notation",
            ),
            (DataType.INT32_ARRAY, [0, (1,)], TypeError, "int32 with tuple"),
            # UINT32 type mixing - within array
            (
                DataType.UINT32_ARRAY,
                [4294967295, "max"],
                TypeError,
                "uint32 with string",
            ),
            (DataType.UINT32_ARRAY, [0, 1.0], TypeError, "uint32 with float"),
            (DataType.UINT32_ARRAY, [1, set()], TypeError, "uint32 with empty set"),
            # INT64 type mixing - within array
            (
                DataType.INT64_ARRAY,
                [-9223372036854775808, "min"],
                TypeError,
                "int64 with string",
            ),
            (
                DataType.INT64_ARRAY,
                [9223372036854775807, 2.0],
                TypeError,
                "int64 with float",
            ),
            (DataType.INT64_ARRAY, [0, b"bytes"], TypeError, "int64 with bytes"),
            # UINT64 type mixing - within array
            (
                DataType.UINT64_ARRAY,
                [18446744073709551615, "max"],
                TypeError,
                "uint64 with string",
            ),
            (DataType.UINT64_ARRAY, [0, 0.0], TypeError, "uint64 with float zero"),
            (
                DataType.UINT64_ARRAY,
                [1, bytearray()],
                TypeError,
                "uint64 with bytearray",
            ),
            # Multiple type mixing - within array
            (
                DataType.INT8_ARRAY,
                [1, "str", 3.14, None],
                TypeError,
                "multiple mixed types",
            ),
            (
                DataType.UINT16_ARRAY,
                [1, "str", 3.14, []],
                TypeError,
                "multiple mixed types",
            ),
            (
                DataType.INT32_ARRAY,
                [1, "str", None, {}],
                TypeError,
                "multiple mixed types",
            ),
        ]

        for dtype, value, expected_error, description in test_cases:
            with self.subTest(dtype=dtype, case=description):
                with self.assertRaises(
                    expected_error,
                    msg=f"Failed to raise {expected_error} for {description}",
                ):
                    dtype.encode(value)

    def test_non_iterable_inputs(self):
        """Test inputs that cannot be iterated over"""
        test_cases = [
            (DataType.INT8_ARRAY, None, TypeError, "None value"),
            (DataType.INT16_ARRAY, 42, TypeError, "single integer"),
            (DataType.UINT32_ARRAY, 3.14, TypeError, "single float"),
            (DataType.INT64_ARRAY, True, TypeError, "single boolean"),
        ]

        for dtype, value, expected_error, description in test_cases:
            with self.subTest(dtype=dtype, case=description):
                with self.assertRaises(
                    expected_error,
                    msg=f"Failed to raise {expected_error} for {description}",
                ):
                    dtype.encode(value)

    def test_invalid_iterable_inputs(self):
        """Test inputs that are iterable but have invalid types or type combinations"""
        test_cases = [
            # Invalid type combinations
            (DataType.INT8_ARRAY, [1, "a", 3], TypeError, "list with mixed types"),
            (DataType.UINT8_ARRAY, [1, None, 3], TypeError, "list with None"),
            (DataType.INT16_ARRAY, [1, 3.14, 2], TypeError, "list with float"),
            (DataType.UINT16_ARRAY, [1, [2], 3], TypeError, "list with nested list"),
            (DataType.UINT32_ARRAY, [1, b"bytes", 3], TypeError, "list with bytes"),
            # Invalid string elements
            (DataType.INT8_ARRAY, ["1", "2", "3"], TypeError, "list of string digits"),
            (DataType.UINT8_ARRAY, ["a", "b", "c"], TypeError, "list of strings"),
            # Invalid container elements
            (DataType.INT16_ARRAY, [{1}, {2}, {3}], TypeError, "list of sets"),
            (DataType.UINT16_ARRAY, [(1,), (2,), (3,)], TypeError, "list of tuples"),
            (DataType.INT32_ARRAY, [{"a": 1}, {"b": 2}], TypeError, "list of dicts"),
            # Complex nested structures
            (DataType.INT8_ARRAY, [[1, 2], [3, 4]], TypeError, "nested number lists"),
            (
                DataType.UINT8_ARRAY,
                [set([1, 2]), set([3, 4])],
                TypeError,
                "list of number sets",
            ),
            (
                DataType.INT16_ARRAY,
                [{"x": 1}, {"y": 2}],
                TypeError,
                "list of number dicts",
            ),
            # Non-numeric types
            (DataType.INT8_ARRAY, [object(), object()], TypeError, "list of objects"),
            (
                DataType.UINT16_ARRAY,
                [lambda x: x, lambda x: x],
                TypeError,
                "list of functions",
            ),
            (
                DataType.INT32_ARRAY,
                [complex(1, 2), complex(3, 4)],
                TypeError,
                "list of complex numbers",
            ),
        ]

        for dtype, value, expected_error, description in test_cases:
            with self.subTest(dtype=dtype, case=description):
                with self.assertRaises(
                    expected_error,
                    msg=f"Failed to raise {expected_error} for {description}",
                ):
                    dtype.encode(value)

    def test_string_array_basic(self):
        """Test string array encoding/decoding for basic cases"""
        test_cases = [
            # Basic cases
            # [],  # Empty array  # This is not a valid test case, as it will be handed in the metric.py to_pb()
            ["Hello", "World"],  # Simple ASCII
            ["Hello", "世界", "👋"],  # Mixed Unicode and emoji
            # Mixed lengths
            ["", "short", "medium" * 10, "long" * 100],
            # Edge cases for individual strings
            ["x" * 65535],  # Max length string
            # Quotes and slashes (safe special chars)
            ['Quote"Quote', "Single'Quote"],  # Quotes
            ["Back\\slash", "Path/slash"],  # Slashes
            # Unicode variations
            ["汉字", "русский", "العربية", "עִבְרִית"],
            ["🌟", "👨‍👩‍👧‍👦", "👨🏻‍💻"],
        ]

        for strings in test_cases:
            with self.subTest(strings=strings):
                encoded = DataType.STRING_ARRAY.encode(strings)
                decoded = cast(List[str], DataType.STRING_ARRAY.decode(encoded))
                self.assertEqual(len(decoded), len(strings))
                self.assertEqual(decoded, strings)

    def test_string_array_empty_strings(self):
        """Test string array encoding/decoding with empty strings"""
        test_cases = [
            ([""], "single empty string"),
            (["", "nonempty"], "empty and nonempty"),
            (["nonempty", ""], "nonempty and empty"),
            (["", "middle", ""], "empty at boundaries"),
            (["nonempty", "", "nonempty"], "empty in middle"),
        ]

        for strings, description in test_cases:
            with self.subTest(case=description):
                # Add print statements for debugging
                print(f"Original strings: {strings}")

                encoded = DataType.STRING_ARRAY.encode(strings)
                print(f"Encoded value: {encoded}")

                decoded = cast(List[str], DataType.STRING_ARRAY.decode(encoded))
                print(f"Decoded strings: {decoded}")

                self.assertEqual(
                    len(decoded), len(strings), f"Length mismatch for {description}"
                )
                self.assertEqual(
                    decoded, strings, f"Content mismatch for {description}"
                )

    def test_string_array_line_endings(self):
        """Test string array encoding/decoding with different line endings"""
        test_cases = [
            # Single line endings
            (["Line1\nLine2", "Line3\nLine4"], "LF only"),
            (["Line1\rLine2", "Line3\rLine4"], "CR only"),
            # Mixed line endings
            (["Line1\r\nLine2"], "CRLF"),
            (["Line1\nLine2", "Line3\rLine4"], "Mixed LF and CR"),
            # Multiple line endings
            (["Line1\n\nLine2"], "Multiple LF"),
            (["Line1\r\rLine2"], "Multiple CR"),
            # Line endings at start/end
            (["\nLine1", "Line2\n"], "LF at boundaries"),
            (["\rLine1", "Line2\r"], "CR at boundaries"),
        ]

        for strings, description in test_cases:
            with self.subTest(case=description):
                encoded = DataType.STRING_ARRAY.encode(strings)
                decoded = cast(List[str], DataType.STRING_ARRAY.decode(encoded))
                self.assertEqual(len(decoded), len(strings))
                self.assertEqual(decoded, strings)

    def test_string_array_special_chars(self):
        """Test string array encoding/decoding with special characters"""
        test_cases = [
            # Control characters
            (["Tab\tText", "Space Text"], "tabs and spaces"),
            (["\b\f\v"], "control characters"),
            # Extended ASCII
            ([chr(i) for i in range(128, 256)], "extended ASCII"),
            # Whitespace combinations
            ([" ", "  ", "\t", "\n", "\r", "\r\n"], "whitespace variants"),
            # Mixed special characters
            (["Mixed\tWith\nMany\rSpecial\fChars"], "mixed special chars"),
            # Zero-width characters
            (["a\u200bb", "a\u200cb"], "zero-width chars"),
            # Combining characters
            (["e\u0301", "n\u0303"], "combining diacritics"),
            # Direction control characters
            (["\u202e\u202dreverse"], "direction controls"),
        ]

        for strings, description in test_cases:
            with self.subTest(case=description):
                encoded = DataType.STRING_ARRAY.encode(strings)
                decoded = cast(List[str], DataType.STRING_ARRAY.decode(encoded))
                self.assertEqual(len(decoded), len(strings))
                self.assertEqual(decoded, strings)

    def test_datetime_array(self):
        """Test datetime array encoding/decoding"""
        base_dt = datetime.now(timezone.utc)
        test_cases = [
            # Basic cases
            [],  # Empty array
            [base_dt],  # Single datetime
            # Historical dates
            [base_dt - timedelta(days=i) for i in range(10)],
            # Future dates
            [base_dt + timedelta(days=i) for i in range(10)],
            # Mix of past and future
            [base_dt + timedelta(days=i) for i in range(-5, 6)],
            # Edge cases
            [
                datetime(1970, 1, 1, tzinfo=timezone.utc),  # Epoch
                datetime(2038, 1, 19, 3, 14, 7, tzinfo=timezone.utc),  # 32-bit limit
                datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),  # Noon UTC
                datetime.now(timezone(timedelta(hours=5))).astimezone(
                    timezone.utc
                ),  # Different timezone
            ],
            # Specific times
            [
                datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),  # Midnight
                datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),  # Noon
                datetime(2024, 1, 1, 23, 59, 59, tzinfo=timezone.utc),  # End of day
            ],
        ]

        for datetimes in test_cases:
            with self.subTest(datetimes=datetimes):
                encoded = DataType.DATETIME_ARRAY.encode(datetimes)
                decoded = cast(List[datetime], DataType.DATETIME_ARRAY.decode(encoded))
                self.assertEqual(len(decoded), len(datetimes))
                for orig, dec in zip(datetimes, decoded):
                    # Truncate to millisecond precision before comparison
                    orig_ts = int(orig.timestamp() * 1000) / 1000
                    dec_ts = int(dec.timestamp() * 1000) / 1000
                    self.assertEqual(orig_ts, dec_ts)


if __name__ == "__main__":
    unittest.main()

"""Unit tests for DataType functionality"""

import math
import unittest
from datetime import datetime, timedelta, timezone
from typing import TypeVar, Union, cast

import numpy as np

from pysparkplug import DataType, Metric, MetricValue, NCmd

SpecificMetricValue = TypeVar("SpecificMetricValue", bound=MetricValue)


def encode_decode(
    value: SpecificMetricValue, datatype: DataType
) -> SpecificMetricValue:
    """Send the value as the specified data type through full serialization stack"""
    metric = Metric(timestamp=0, name="test", datatype=datatype, value=value)
    n_cmd = NCmd(timestamp=0, metrics=(metric,))
    raw = n_cmd.encode(include_dtypes=True)
    other_n_cmd = NCmd.decode(raw=raw)
    other_metric = other_n_cmd.metrics[0]
    return cast(SpecificMetricValue, other_metric.value)


def check_float(
    test_case: unittest.TestCase, value: float, expected: float, datatype: DataType
) -> None:
    if math.isnan(expected):
        test_case.assertTrue(
            math.isnan(value), f"Expected NaN, got {value} for {datatype}"
        )
    elif math.isinf(expected):
        test_case.assertTrue(
            math.isinf(value),
            f"Expected {expected}, got {value} for {datatype}",
        )
        # Check sign of infinity
        test_case.assertEqual(
            math.copysign(1, expected),
            math.copysign(1, value),
            f"Infinity sign mismatch for {datatype}",
        )
    else:
        # For normal numbers, compare with relative tolerance
        test_case.assertAlmostEqual(
            value,
            expected,
            delta=delta(
                expected, single=datatype in {DataType.FLOAT, DataType.FLOAT_ARRAY}
            ),
            msg=f"Value mismatch for {datatype}: expected {expected}, got {value}",
        )
        # Check sign of zero
        if expected == 0:
            test_case.assertEqual(
                math.copysign(1, expected),
                math.copysign(1, value),
                f"Zero sign mismatch for {datatype}",
            )


def delta(value: Union[float, np.single], single: bool = False):
    """Expected float precision error for this value"""
    if single:
        value = np.single(value)
    return np.nextafter(value, np.inf) - value


class TestScalarTypes(unittest.TestCase):
    """Test scalar datatype functionality"""

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
                    decoded = encode_decode(value, datatype=dtype)
                    self.assertEqual(
                        decoded, value, f"Failed to encode/decode {value} with {dtype}"
                    )

    def test_decoder_errors(self) -> None:
        with self.assertRaises(OverflowError):
            # too large
            DataType.INT8.decode(2**9)

        with self.assertRaises(ValueError):
            # not enough bytes
            DataType.INT16_ARRAY.decode(b"\x00")

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
                decoded = cast(float, encode_decode(value, datatype=dtype))
                check_float(self, decoded, value, dtype)

    def test_datetime_encoding(self):
        """Test datetime encoding/decoding with timezones"""
        test_cases = [
            # UTC timezone
            (datetime(2023, 1, 1, tzinfo=timezone.utc), 1672531200000),
            # Non-UTC timezone
            (
                datetime(2023, 1, 1, 12, 0, tzinfo=timezone(timedelta(hours=5))),
                1672556400000,  # 2023-01-01 07:00:00 UTC
            ),
            # Timezone naive
            (datetime(2023, 1, 1), None),
            # Edge cases
            (datetime(1970, 1, 1, tzinfo=timezone.utc), 0),  # Epoch
            (
                datetime(2038, 1, 19, 3, 14, 7, tzinfo=timezone.utc),
                2147483647000,
            ),  # 32-bit limit (2^31 - 1 seconds)
        ]

        for value, expected in test_cases:
            with self.subTest(datetime=value):
                encoded = DataType.DATETIME.encode(value)
                if expected is not None:
                    self.assertEqual(encoded, expected)
                decoded = cast(datetime, encode_decode(value, DataType.DATETIME))
                self.assertLess(abs(decoded.timestamp() - value.timestamp()), 1e-3)

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
            "x" * 1000,  # Large string
            "x" * 10000,  # XL string
            "x" * 65535,  # exactly at UINT16_MAX
            "x" * 65536,  # exceeding UINT16_MAX
            "x" * 100000,  # XXL string
            "世界" * 32767,  # Just under UINT16_MAX in UTF-8 bytes
        ]

        for text in test_cases:
            with self.subTest(text=text[:50] + "..." if len(text) > 50 else text):
                decoded = cast(str, encode_decode(text, DataType.TEXT))
                self.assertEqual(decoded, text)

    def test_not_implemented(self) -> None:
        with self.assertRaises(NotImplementedError):
            DataType.TEMPLATE.field

        with self.assertRaises(NotImplementedError):
            DataType.TEMPLATE.encode(0)

        with self.assertRaises(NotImplementedError):
            DataType.TEMPLATE.decode(0)


class TestArrayTypes(unittest.TestCase):
    """Test array type functionality"""

    def test_integer_array_validation(self):
        """Test integer array validation with boundaries and overflow cases"""
        test_cases = [
            # INT8 (-128 to 127)
            (DataType.INT8_ARRAY, (-128,), None),  # Min value
            (DataType.INT8_ARRAY, (127,), None),  # Max value
            (DataType.INT8_ARRAY, (-128, -1, 0, 1, 127), None),  # Range of values
            (DataType.INT8_ARRAY, (-129,), ValueError),  # Below min
            (DataType.INT8_ARRAY, (128,), ValueError),  # Above max
            (DataType.INT8_ARRAY, (-128, 128), ValueError),  # Valid and invalid
            # UINT8 (0 to 255)
            (DataType.UINT8_ARRAY, (0,), None),  # Min value
            (DataType.UINT8_ARRAY, (255,), None),  # Max value
            (DataType.UINT8_ARRAY, (0, 1, 128, 255), None),  # Range of values
            (DataType.UINT8_ARRAY, (-1,), ValueError),  # Below min
            (DataType.UINT8_ARRAY, (256,), ValueError),  # Above max
            (DataType.UINT8_ARRAY, (0, 256), ValueError),  # Valid and invalid
            # INT16 (-32768 to 32767)
            (DataType.INT16_ARRAY, (-32768,), None),  # Min value
            (DataType.INT16_ARRAY, (32767,), None),  # Max value
            (DataType.INT16_ARRAY, (-32768, -1, 0, 1, 32767), None),  # Range of values
            (DataType.INT16_ARRAY, (-32769,), ValueError),  # Below min
            (DataType.INT16_ARRAY, (32768,), ValueError),  # Above max
            (DataType.INT16_ARRAY, (-32768, 32768), ValueError),  # Valid and invalid
            # UINT16 (0 to 65535)
            (DataType.UINT16_ARRAY, (0,), None),  # Min value
            (DataType.UINT16_ARRAY, (65535,), None),  # Max value
            (DataType.UINT16_ARRAY, (0, 1, 32768, 65535), None),  # Range of values
            (DataType.UINT16_ARRAY, (-1,), ValueError),  # Below min
            (DataType.UINT16_ARRAY, (65536,), ValueError),  # Above max
            (DataType.UINT16_ARRAY, (0, 65536), ValueError),  # Valid and invalid
            # INT32 (-2147483648 to 2147483647)
            (DataType.INT32_ARRAY, (-2147483648,), None),  # Min value
            (DataType.INT32_ARRAY, (2147483647,), None),  # Max value
            (
                DataType.INT32_ARRAY,
                (-2147483648, -1, 0, 1, 2147483647),
                None,
            ),  # Range of values
            (DataType.INT32_ARRAY, (-2147483649,), ValueError),  # Below min
            (DataType.INT32_ARRAY, (2147483648,), ValueError),  # Above max
            (
                DataType.INT32_ARRAY,
                (-2147483648, 2147483648),
                ValueError,
            ),  # Valid and invalid
            # UINT32 (0 to 4294967295)
            (DataType.UINT32_ARRAY, (0,), None),  # Min value
            (DataType.UINT32_ARRAY, (4294967295,), None),  # Max value
            (
                DataType.UINT32_ARRAY,
                (0, 1, 2147483648, 4294967295),
                None,
            ),  # Range of values
            (DataType.UINT32_ARRAY, (-1,), ValueError),  # Below min
            (DataType.UINT32_ARRAY, (4294967296,), ValueError),  # Above max
            (
                DataType.UINT32_ARRAY,
                (0, 4294967296),
                ValueError,
            ),  # Valid and invalid
            # INT64 (-9223372036854775808 to 9223372036854775807)
            (DataType.INT64_ARRAY, (-9223372036854775808,), None),  # Min value
            (DataType.INT64_ARRAY, (9223372036854775807,), None),  # Max value
            (
                DataType.INT64_ARRAY,
                (-9223372036854775808, -1, 0, 1, 9223372036854775807),
                None,
            ),  # Range
            (DataType.INT64_ARRAY, (-9223372036854775809,), ValueError),  # Below min
            (DataType.INT64_ARRAY, (9223372036854775808,), ValueError),  # Above max
            (
                DataType.INT64_ARRAY,
                (-9223372036854775808, 9223372036854775808),
                ValueError,
            ),  # Valid and invalid
            # UINT64 (0 to 18446744073709551615)
            (DataType.UINT64_ARRAY, (0,), None),  # Min value
            (DataType.UINT64_ARRAY, (18446744073709551615,), None),  # Max value
            (
                DataType.UINT64_ARRAY,
                (0, 1, 9223372036854775808, 18446744073709551615),
                None,
            ),  # Range
            (DataType.UINT64_ARRAY, (-1,), ValueError),  # Below min
            (DataType.UINT64_ARRAY, (18446744073709551616,), ValueError),  # Above max
            (
                DataType.UINT64_ARRAY,
                (0, 18446744073709551616),
                ValueError,
            ),  # Valid and invalid
        ]

        for dtype, value, expected_error in test_cases:
            with self.subTest(dtype=dtype, value=value):
                if expected_error is None:
                    decoded = encode_decode(value, dtype)
                    self.assertEqual(decoded, value)
                else:
                    with self.assertRaises(expected_error):
                        dtype.encode(value)

    def test_float_array_validation(self):
        """Test floating point array validation"""
        test_cases = [
            # FLOAT basic cases
            (DataType.FLOAT_ARRAY, (0.0,)),  # Zero
            (DataType.FLOAT_ARRAY, (-1.0, 1.0)),  # Unit values
            (DataType.FLOAT_ARRAY, (3.14159, -3.14159)),  # Common pi
            # FLOAT boundary cases
            (DataType.FLOAT_ARRAY, (3.4028235e38,)),  # Max float32
            (DataType.FLOAT_ARRAY, (-3.4028235e38,)),  # Min float32
            (DataType.FLOAT_ARRAY, (1.17549435e-38,)),  # Min positive normal
            (DataType.FLOAT_ARRAY, (1.4e-45,)),  # Min positive subnormal
            # FLOAT special values
            (DataType.FLOAT_ARRAY, (float("inf"),)),
            (DataType.FLOAT_ARRAY, (float("-inf"),)),
            (DataType.FLOAT_ARRAY, (float("nan"),)),
            (DataType.FLOAT_ARRAY, (float("inf"), float("-inf"), float("nan"))),
            # FLOAT mixed values
            (DataType.FLOAT_ARRAY, (1, 1.0, 1.5)),  # Mixed integers and floats
            (DataType.FLOAT_ARRAY, (-3.4028235e38, 0.0, 3.4028235e38)),  # Range
            # DOUBLE basic cases
            (DataType.DOUBLE_ARRAY, (0.0,)),  # Zero
            (DataType.DOUBLE_ARRAY, (-1.0, 1.0)),  # Unit values
            (DataType.DOUBLE_ARRAY, (math.pi, -math.pi)),  # Pi
            # DOUBLE boundary cases
            (DataType.DOUBLE_ARRAY, (1.7976931348623157e308,)),  # Max double
            (DataType.DOUBLE_ARRAY, (-1.7976931348623157e308,)),  # Min double
            (
                DataType.DOUBLE_ARRAY,
                (2.2250738585072014e-308,),
            ),  # Min positive normal
            (
                DataType.DOUBLE_ARRAY,
                (4.9406564584124654e-324,),
            ),  # Min positive subnormal
            # DOUBLE special values
            (DataType.DOUBLE_ARRAY, (float("inf"),)),
            (DataType.DOUBLE_ARRAY, (float("-inf"),)),
            (DataType.DOUBLE_ARRAY, (float("nan"),)),
            (DataType.DOUBLE_ARRAY, (float("inf"), float("-inf"), float("nan"))),
            # DOUBLE mixed values
            (DataType.DOUBLE_ARRAY, (1, 1.0, 1.5)),  # Mixed integers and floats
            (
                DataType.DOUBLE_ARRAY,
                (-1.7976931348623157e308, 0.0, 1.7976931348623157e308),
            ),  # Range
            # Testing precision
            (DataType.FLOAT_ARRAY, (1.23456789,)),  # Beyond float32 precision
            (
                DataType.DOUBLE_ARRAY,
                (1.234567890123456789,),
            ),  # Beyond float64 precision
        ]

        for dtype, value in test_cases:
            with self.subTest(dtype=dtype, value=value):
                decoded = encode_decode(value, dtype)
                self.assertEqual(len(decoded), len(value))
                for orig, dec in zip(value, decoded):
                    check_float(self, dec, orig, dtype)

    def test_integer_array_type_errors(self):
        """Test integer array validation with invalid type combinations"""
        test_cases = [
            # INT8 type mixing - within array
            (DataType.INT8_ARRAY, (-128, "string"), ValueError, "int8 with string"),
            (DataType.INT8_ARRAY, (127, 3.14), ValueError, "int8 with float"),
            (DataType.INT8_ARRAY, (0, None), ValueError, "int8 with None"),
            (DataType.INT8_ARRAY, (0, [1]), ValueError, "int8 with list"),
            (DataType.INT8_ARRAY, (0, {}), ValueError, "int8 with dict"),
            # UINT8 type mixing - within array
            (DataType.UINT8_ARRAY, (255, "abc"), ValueError, "uint8 with string"),
            (DataType.UINT8_ARRAY, (0, 1.5), ValueError, "uint8 with float"),
            (DataType.UINT8_ARRAY, (128, None), ValueError, "uint8 with None"),
            (DataType.UINT8_ARRAY, (0, (1,)), ValueError, "uint8 with tuple"),
            # INT16 type mixing - within array
            (DataType.INT16_ARRAY, (-32768, "xyz"), ValueError, "int16 with string"),
            (DataType.INT16_ARRAY, (32767, 2.718), ValueError, "int16 with float"),
            (DataType.INT16_ARRAY, (0, {}), ValueError, "int16 with dict"),
            (DataType.INT16_ARRAY, (0, set((1,))), ValueError, "int16 with set"),
            # UINT16 type mixing - within array
            (DataType.UINT16_ARRAY, (65535, "test"), ValueError, "uint16 with string"),
            (DataType.UINT16_ARRAY, (0, 3.14159), ValueError, "uint16 with float"),
            (DataType.UINT16_ARRAY, (1, []), ValueError, "uint16 with empty list"),
            # INT32 type mixing - within array
            (
                DataType.INT32_ARRAY,
                (-2147483648, "large"),
                ValueError,
                "int32 with string",
            ),
            (
                DataType.INT32_ARRAY,
                (2147483647, 1.23e5),
                ValueError,
                "int32 with scientific notation",
            ),
            (DataType.INT32_ARRAY, (0, (1,)), ValueError, "int32 with tuple"),
            # UINT32 type mixing - within array
            (
                DataType.UINT32_ARRAY,
                (4294967295, "max"),
                ValueError,
                "uint32 with string",
            ),
            (DataType.UINT32_ARRAY, (0, 1.0), ValueError, "uint32 with float"),
            (DataType.UINT32_ARRAY, (1, set()), ValueError, "uint32 with empty set"),
            # INT64 type mixing - within array
            (
                DataType.INT64_ARRAY,
                (-9223372036854775808, "min"),
                ValueError,
                "int64 with string",
            ),
            (
                DataType.INT64_ARRAY,
                (9223372036854775807, 2.0),
                ValueError,
                "int64 with float",
            ),
            (DataType.INT64_ARRAY, (0, b"bytes"), ValueError, "int64 with bytes"),
            # UINT64 type mixing - within array
            (
                DataType.UINT64_ARRAY,
                (18446744073709551615, "max"),
                ValueError,
                "uint64 with string",
            ),
            (DataType.UINT64_ARRAY, (0, 0.0), ValueError, "uint64 with float zero"),
            (
                DataType.UINT64_ARRAY,
                (1, bytearray()),
                ValueError,
                "uint64 with bytearray",
            ),
            # Multiple type mixing - within array
            (
                DataType.INT8_ARRAY,
                (1, "str", 3.14, None),
                ValueError,
                "multiple mixed types",
            ),
            (
                DataType.UINT16_ARRAY,
                (1, "str", 3.14, []),
                ValueError,
                "multiple mixed types",
            ),
            (
                DataType.INT32_ARRAY,
                (1, "str", None, {}),
                ValueError,
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
            (DataType.UINT64_ARRAY, True, TypeError, "single boolean"),
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
            (DataType.INT8_ARRAY, (1, "a", 3), ValueError, "mixed types"),
            (DataType.UINT8_ARRAY, (1, None, 3), ValueError, "None"),
            (DataType.INT16_ARRAY, (1, 3.14, 2), ValueError, "float"),
            (DataType.UINT16_ARRAY, (1, [2], 3), ValueError, "nested list"),
            (DataType.UINT32_ARRAY, (1, b"bytes", 3), ValueError, "bytes"),
            # Invalid string elements
            (DataType.INT8_ARRAY, ("1", "2", "3"), ValueError, "string digits"),
            (DataType.UINT8_ARRAY, ("a", "b", "c"), ValueError, "strings"),
            # Invalid container elements
            (DataType.INT16_ARRAY, ({1}, {2}, {3}), ValueError, "sets"),
            (DataType.UINT16_ARRAY, ((1,), (2,), (3,)), ValueError, "tuples"),
            (DataType.INT32_ARRAY, ({"a": 1}, {"b": 2}), ValueError, "dicts"),
            # Complex nested structures
            (DataType.INT8_ARRAY, ((1, 2), (3, 4)), ValueError, "nested structure"),
            (
                DataType.UINT8_ARRAY,
                (set((1, 2)), set((3, 4))),
                ValueError,
                "number sets",
            ),
            (
                DataType.INT16_ARRAY,
                ({"x": 1}, {"y": 2}),
                ValueError,
                "number dicts",
            ),
            # Non-numeric types
            (DataType.INT8_ARRAY, (object(), object()), ValueError, "objects"),
            (
                DataType.UINT16_ARRAY,
                (lambda x: x, lambda x: x),
                ValueError,
                "functions",
            ),
            (
                DataType.INT32_ARRAY,
                (complex(1, 2), complex(3, 4)),
                ValueError,
                "complex numbers",
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
            ("Hello", "World"),  # Simple ASCII
            ("Hello", "世界", "👋"),  # Mixed Unicode and emoji
            # Mixed lengths
            ("", "short", "medium" * 10, "long" * 100),
            # Edge cases for individual strings
            ("x" * 65535,),  # Max length string
            # Quotes and slashes (safe special chars)
            ('Quote"Quote', "Single'Quote"),  # Quotes
            ("Back\\slash", "Path/slash"),  # Slashes
            # Unicode variations
            ("汉字", "русский", "العربية", "עִבְרִית"),
            ("🌟", "👨‍👩‍👧‍👦", "👨🏻‍💻"),
        ]

        for strings in test_cases:
            with self.subTest(strings=strings):
                decoded = encode_decode(strings, DataType.STRING_ARRAY)
                self.assertEqual(len(decoded), len(strings))
                self.assertEqual(decoded, strings)

    def test_string_array_empty_strings(self):
        """Test string array encoding/decoding with empty strings"""
        test_cases = [
            (("",), "single empty string"),
            (("", "nonempty"), "empty and nonempty"),
            (("nonempty", ""), "nonempty and empty"),
            (("", "middle", ""), "empty at boundaries"),
            (("nonempty", "", "nonempty"), "empty in middle"),
        ]

        for strings, description in test_cases:
            with self.subTest(case=description):
                decoded = encode_decode(strings, DataType.STRING_ARRAY)
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
            (("Line1\nLine2", "Line3\nLine4"), "LF only"),
            (("Line1\rLine2", "Line3\rLine4"), "CR only"),
            # Mixed line endings
            (("Line1\r\nLine2",), "CRLF"),
            (("Line1\nLine2", "Line3\rLine4"), "Mixed LF and CR"),
            # Multiple line endings
            (("Line1\n\nLine2",), "Multiple LF"),
            (("Line1\r\rLine2",), "Multiple CR"),
            # Line endings at start/end
            (("\nLine1", "Line2\n"), "LF at boundaries"),
            (("\rLine1", "Line2\r"), "CR at boundaries"),
        ]

        for strings, description in test_cases:
            with self.subTest(case=description):
                decoded = encode_decode(strings, DataType.STRING_ARRAY)
                self.assertEqual(len(decoded), len(strings))
                self.assertEqual(decoded, strings)

    def test_string_array_special_chars(self):
        """Test string array encoding/decoding with special characters"""
        test_cases = [
            # Control characters
            (("Tab\tText", "Space Text"), "tabs and spaces"),
            (("\b\f\v",), "control characters"),
            # Extended ASCII
            (tuple(chr(i) for i in range(128, 256)), "extended ASCII"),
            # Whitespace combinations
            ((" ", "  ", "\t", "\n", "\r", "\r\n"), "whitespace variants"),
            # Mixed special characters
            (("Mixed\tWith\nMany\rSpecial\fChars",), "mixed special chars"),
            # Zero-width characters
            (("a\u200bb", "a\u200cb"), "zero-width chars"),
            # Combining characters
            (("e\u0301", "n\u0303"), "combining diacritics"),
            # Direction control characters
            (("\u202e\u202dreverse",), "direction controls"),
        ]

        for strings, description in test_cases:
            with self.subTest(case=description):
                decoded = encode_decode(strings, DataType.STRING_ARRAY)
                self.assertEqual(len(decoded), len(strings))
                self.assertEqual(decoded, strings)

    def test_boolean_array(self) -> None:
        """Test boolean array encoding/decoding"""
        test_cases = (
            ((), "Empty"),
            ((True,), "Single true"),
            ((False,), "Single false"),
            ((True, False, True, True), "Short array"),
            (
                (
                    True,
                    False,
                )
                * 2**8,
                "Long array",
            ),
        )
        for array, description in test_cases:
            with self.subTest(case=description):
                decoded = encode_decode(array, DataType.BOOLEAN_ARRAY)
                self.assertEqual(len(decoded), len(array))
                self.assertEqual(decoded, array)

    def test_datetime_array(self):
        """Test datetime array encoding/decoding"""
        base_dt = datetime.now(timezone.utc)
        test_cases = [
            # Basic cases
            (),  # Empty array
            (base_dt,),  # Single datetime
            # Historical dates
            tuple(base_dt - timedelta(days=i) for i in range(10)),
            # Future dates
            tuple(base_dt + timedelta(days=i) for i in range(10)),
            # Mix of past and future
            tuple(base_dt + timedelta(days=i) for i in range(-5, 6)),
            # Edge cases
            (
                datetime(1970, 1, 1, tzinfo=timezone.utc),  # Epoch
                datetime(2038, 1, 19, 3, 14, 7, tzinfo=timezone.utc),  # 32-bit limit
                datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),  # Noon UTC
                datetime.now(timezone(timedelta(hours=5))).astimezone(
                    timezone.utc
                ),  # Different timezone
            ),
            # Specific times
            (
                datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),  # Midnight
                datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),  # Noon
                datetime(2024, 1, 1, 23, 59, 59, tzinfo=timezone.utc),  # End of day
            ),
            # Timezone naive datetime objects
            (
                datetime(2024, 1, 1, 0, 0, 0),  # Midnight
                datetime(2024, 1, 1, 12, 0, 0),  # Noon
                datetime(2024, 1, 1, 23, 59, 59),  # End of day
            ),
            # Non-UTC timezones
            (
                datetime(
                    2024, 1, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=5))
                ),  # Midnight
                datetime(
                    2024, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=5))
                ),  # Noon
                datetime(
                    2024, 1, 1, 23, 59, 59, tzinfo=timezone(timedelta(hours=5))
                ),  # End of day
            ),
        ]

        for datetimes in test_cases:
            with self.subTest(datetimes=datetimes):
                decoded = encode_decode(datetimes, DataType.DATETIME_ARRAY)
                self.assertEqual(len(decoded), len(datetimes))
                for orig, dec in zip(datetimes, decoded):
                    self.assertLess(abs(dec.timestamp() - orig.timestamp()), 1e-3)

    def test_specification_examples(self) -> None:
        test_cases = (
            (DataType.INT8_ARRAY, (-23, 123), bytes((0xE9, 0x7B))),
            (DataType.INT16_ARRAY, (-30_000, 30_000), bytes((0xD0, 0x8A, 0x30, 0x75))),
            (
                DataType.INT32_ARRAY,
                (-1, 315338746),
                bytes((0xFF, 0xFF, 0xFF, 0xFF, 0xFA, 0xAF, 0xCB, 0x12)),
            ),
            (
                DataType.INT64_ARRAY,
                (-4270929666821191986, -3601064768563266876),
                bytes(
                    (
                        0xCE,
                        0x06,
                        0x72,
                        0xAC,
                        0x18,
                        0x9C,
                        0xBA,
                        0xC4,
                        0xC4,
                        0xBA,
                        0x9C,
                        0x18,
                        0xAC,
                        0x72,
                        0x06,
                        0xCE,
                    )
                ),
            ),
            (DataType.UINT8_ARRAY, (23, 250), bytes((0x17, 0xFA))),
            (DataType.UINT16_ARRAY, (30, 52360), bytes((0x1E, 0x00, 0x88, 0xCC))),
            (
                DataType.UINT32_ARRAY,
                (52, 3293969225),
                bytes((0x34, 0x00, 0x00, 0x00, 0x49, 0xFB, 0x55, 0xC4)),
            ),
            (
                DataType.UINT64_ARRAY,
                (52, 16444743074749521625),
                bytes(
                    (
                        0x34,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0xD9,
                        0x9E,
                        0x02,
                        0xD1,
                        0xB2,
                        0x76,
                        0x37,
                        0xE4,
                    )
                ),
            ),
            (
                DataType.FLOAT_ARRAY,
                (1.23, 89.341),
                bytes((0xA4, 0x70, 0x9D, 0x3F, 0x98, 0xAE, 0xB2, 0x42)),
            ),
            (
                DataType.DOUBLE_ARRAY,
                (12.354213, 1022.9123213),
                bytes(
                    (
                        0xD7,
                        0xA2,
                        0x05,
                        0x68,
                        0x5B,
                        0xB5,
                        0x28,
                        0x40,
                        0x8E,
                        0x17,
                        0x1C,
                        0x6F,
                        0x4C,
                        0xF7,
                        0x8F,
                        0x40,
                    )
                ),
            ),
            (
                DataType.BOOLEAN_ARRAY,
                (
                    False,
                    False,
                    True,
                    True,
                    False,
                    True,
                    False,
                    False,
                    True,
                    True,
                    False,
                    True,
                ),
                bytes((0x0C, 0x00, 0x00, 0x00, 0x34, 0xD0)),
            ),
            (
                DataType.STRING_ARRAY,
                ("ABC", "hello"),
                bytes((0x41, 0x42, 0x43, 0x00, 0x68, 0x65, 0x6C, 0x6C, 0x6F, 0x00)),
            ),
            (
                DataType.DATETIME_ARRAY,
                (
                    datetime(2009, 10, 21, 5, 27, 55, 335_000, tzinfo=timezone.utc),
                    datetime(2022, 6, 24, 21, 57, 55, tzinfo=timezone.utc),
                ),
                bytes(
                    (
                        0xC7,
                        0xD0,
                        0x90,
                        0x75,
                        0x24,
                        0x01,
                        0x00,
                        0x00,
                        0xB8,
                        0xBA,
                        0xB8,
                        0x97,
                        0x81,
                        0x01,
                        0x00,
                        0x00,
                    )
                ),
            ),
        )
        for datatype, value, expected_bytes in test_cases:
            with self.subTest(datatype=datatype):
                actual_bytes = datatype.encode(value)
                self.assertEqual(expected_bytes, actual_bytes)

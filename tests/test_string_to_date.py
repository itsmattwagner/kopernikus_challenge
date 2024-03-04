from datetime import datetime

import pytest

from src.utils.load_data import string_to_date


def test_string_to_date_with_timestamp():
    """Tests string_to_date function with a timestamp string."""
    timestamp_str = "1616778760501"
    expected_date = datetime(2021, 3, 26, 18, 12, 40, 501000)
    assert string_to_date(timestamp_str) == expected_date


def test_string_to_date_with_custom_format():
    """Tests string_to_date function with a custom formatted date string."""
    date_str = "2021_03_26__07_41_30"
    expected_date = datetime(2021, 3, 26, 7, 41, 30)
    assert string_to_date(date_str) == expected_date


def test_string_to_date_with_invalid_string():
    """Tests string_to_date function with an invalid string, expecting a ValueError."""
    invalid_str = "invalid_date_string"
    with pytest.raises(ValueError):
        string_to_date(invalid_str)


def test_string_to_date_with_edge_cases():
    """Tests string_to_date function with edge case inputs."""
    # Edge cases could include things like empty strings, strings that are just on the edge of valid, etc.
    # Here's an example with an empty string:
    with pytest.raises(ValueError):
        string_to_date("")


def compare_datestrings():
    """Tests if the return type of string_to_date function is able to be compared with each other for sorting."""

    date_str1 = "2021_03_26__07_41_30"
    date_str2 = "2021_03_27__07_41_30"
    assert string_to_date(date_str1) < string_to_date(date_str2)

    date_str3 = "1616778760501"
    date_str4 = "1616778760502"
    assert string_to_date(date_str3) < string_to_date(date_str4)

    assert string_to_date(date_str1) < string_to_date(date_str3)
    assert string_to_date(date_str2) < string_to_date(date_str4)
    assert string_to_date(date_str1) < string_to_date(date_str4)
    assert string_to_date(date_str2) < string_to_date(date_str3)

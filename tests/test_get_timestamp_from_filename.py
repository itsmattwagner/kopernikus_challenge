import pytest

from src.utils.load_data import get_timestamp_from_filename


def test_get_timestamp_from_filename_with_first_format():
    """Tests the function for the first format of the timestamp."""
    filename = "c20_2021_03_26__07_41_30.png"
    assert get_timestamp_from_filename(filename) == "2021_03_26__07_41_30"


def test_get_timestamp_from_filename_with_second_format():
    """Tests the function for filenames with a UNIX timestamp."""
    filename = "c21-1616778760501.png"
    assert get_timestamp_from_filename(filename) == "1616778760501"


def test_with_empty_string():
    with pytest.raises(ValueError):
        get_timestamp_from_filename("")

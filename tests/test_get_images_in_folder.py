from typing import List

import pytest

from src.utils.load_data import get_images_in_folder, get_timestamp_from_filename


def test_get_images_in_folder_with_ordered_list():
    """Tests if the new list for a camera id is sorted by timestamp ascending."""
    data_path: str = "data/dataset/"
    files_by_camera_id: dict = get_images_in_folder(data_path)

    timestamps: List[int] = [
        int(get_timestamp_from_filename(filename))
        for filename in files_by_camera_id["c10"]
    ]

    assert sorted(timestamps) == timestamps


def test_get_images_in_folder_with_empty_dir(tmp_path):
    """Tests if the function raises ValueError if given an empty directory."""
    data_path = tmp_path / "sub"
    data_path.mkdir()

    with pytest.raises(ValueError):
        get_images_in_folder(data_path)

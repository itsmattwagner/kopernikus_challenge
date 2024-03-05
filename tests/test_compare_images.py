# TODO add test that checks if after compare_images the sum is the same as the sum of the input for each camera_id

import pytest

from src.utils.handle_files import compare_images_parallel
from src.utils.load_data import get_images_in_folder


def test_compare_images_with_length():
    data_path = "data/dataset/"
    files_by_camera_id = get_images_in_folder(data_path)

    # call compare_image with files_by_camera_id and args parameters
    delete_frame, keep_frames = compare_images_parallel(files_by_camera_id, data_path)

    # sum of all frames in delete_frame
    sum_delete_frame = 0
    for camera_id in delete_frame:
        sum_delete_frame += len(delete_frame[camera_id])

    # sum of all frames in keep_frames
    sum_keep_frames = 0
    for camera_id in keep_frames:
        sum_keep_frames += len(keep_frames[camera_id])

    # sum of all frames in files_by_camera_id
    sum_files_by_camera_id = 0
    for camera_id in files_by_camera_id:
        sum_files_by_camera_id += len(files_by_camera_id[camera_id])

    assert sum_delete_frame + sum_keep_frames == sum_files_by_camera_id

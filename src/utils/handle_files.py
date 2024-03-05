import errno
import os
from pathlib import Path
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np

from src.utils.kopernikus_func import (
    compare_frames_change_detection,
    preprocess_image_change_detection,
)


# TODO may have to adjust default values for gaussian_blur_radius_list and min_contour_area
def compare_images(
    files_by_camera_id: Dict[str, List[str]],
    data_path: Union[str, Path],
    gaussian_blur_radius_list: Tuple[int] = (5, 11, 21),
    min_contour_area: Union[int, float] = 500,
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """The function compares images and returns a dict of images to delete and \
        a dict of images grouped by camera_id to keep.

    Args:
        files_by_camera_id (Dict[str, List[str]]): A dictionary with the camera_id as key and a list of filenames from \
            that camera as value.
        data_path (str | Path): The data path to the folder to search for the camera images.
        gaussian_blur_radius_list (Tuple[int], optional): Gaussian blur radii for preprocess_image_change_detection(). \
            Defaults to (5, 11, 21).
        min_contour_area (int | float, optional): The min area for contours to be considered. Defaults to 500.

    Raises:
        FileNotFoundError: _description_
        FileNotFoundError: _description_

    Returns:
        List[Dict[str, List[str]], Dict[str, List[str]]]: A list with two dictionaries. The first dictionary  \
            contains the filenames to delete and the second dictionary contains the filenames to keep.
    """

    # return dict with camera_ids as keys and filenames are values
    delete_images: Dict[str, List[str]] = dict()
    keep_images: Dict[str, List[str]] = dict()

    # threshold when an image is considered to be the same as the previous one
    score_threshold: int = 100

    # iterate over keys in files_by_camera_id
    for camera_id in files_by_camera_id:

        prev_frame_same: bool = False

        # iterate over values in files_by_camera_id
        for i in range(len(files_by_camera_id[camera_id]) - 1):
            # i: int = 0
            # while i < len(files_by_camera_id[camera_id]) - 1:

            # load image
            prev_frame_path: Path = os.path.join(
                data_path, files_by_camera_id[camera_id][i]
            )
            next_frame_path: Path = os.path.join(
                data_path, files_by_camera_id[camera_id][i + 1]
            )

            prev_frame: np.ndarray = cv2.imread(prev_frame_path)
            next_frame: np.ndarray = cv2.imread(next_frame_path)

            if prev_frame is None:
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), prev_frame_path
                )
            if next_frame is None:
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), next_frame_path
                )

            # preprocess frames
            # TODO find good value for gaussion blur radii and add to cli parameters
            mask: Tuple[int] = (0, 0, 0, 0)  # images should remain unchanged
            prev_frame = preprocess_image_change_detection(
                prev_frame,
                gaussian_blur_radius_list=gaussian_blur_radius_list,
                black_mask=mask,
            )
            next_frame = preprocess_image_change_detection(
                next_frame,
                gaussian_blur_radius_list=gaussian_blur_radius_list,
                black_mask=mask,
            )

            # resize frames if shape is not the same (larger to smaller)
            if prev_frame.shape != next_frame.shape:
                # reshape to smaller image
                if prev_frame.shape[0] > next_frame.shape[0]:
                    prev_frame = cv2.resize(
                        prev_frame, (next_frame.shape[1], next_frame.shape[0])
                    )
                else:
                    next_frame = cv2.resize(
                        next_frame, (prev_frame.shape[1], prev_frame.shape[0])
                    )

            # compare images
            # TODO find good value for min_contour_area add to cli parameters
            score, _, _ = compare_frames_change_detection(
                prev_frame, next_frame, min_contour_area=min_contour_area
            )

            # if score is low enough, delete prev_frame
            if score < score_threshold:
                # add to delete_images
                if camera_id not in delete_images:
                    delete_images[camera_id] = []

                delete_images[camera_id].append(files_by_camera_id[camera_id][i])
            else:
                # if the previous frame was already considered to be the same as the next (now), add now to keep_images
                if prev_frame_same:
                    if camera_id not in delete_images:
                        delete_images[camera_id] = []
                    delete_images[camera_id].append(files_by_camera_id[camera_id][i])
                    prev_frame_same = False
                    # i += 1
                    continue

                if camera_id not in keep_images:
                    keep_images[camera_id] = []

                keep_images[camera_id].append(files_by_camera_id[camera_id][i])

                prev_frame_same = True

            if i + 1 == len(files_by_camera_id[camera_id]):
                if prev_frame_same:
                    delete_images[camera_id].append(
                        files_by_camera_id[camera_id][i + 1]
                    )
                else:
                    keep_images[camera_id].append(files_by_camera_id[camera_id][i + 1])

            # i += 1

    return delete_images, keep_images

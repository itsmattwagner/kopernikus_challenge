import errno
import logging
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np

from src.utils.kopernikus_func import (
    compare_frames_change_detection,
    preprocess_image_change_detection,
)


def remove_images(
    delete_images: Dict[str, List[str]], data_path: Union[str, Path]
) -> None:
    """The function removes images from the data_path that are provided by the dictionary.

    Args:
        delete_images (Dict[str, List[str]]): A dictionary with the camera_id as key and a list of filenames from \
            that camera as value.
        data_path (str | Path): The data path to the folder to search for the camera images.
    """
    # remove images from data_path
    for _, filenames in delete_images.items():
        for filename in filenames:
            img_path: Path = os.path.join(data_path, filename)

            # remove img_path
            cmd = ["rm", str(img_path)]
            subprocess.run(cmd, check=True)


def copy_images(
    filenames: List[str],
    data_path: Union[str, Path],
    unique_images_path: str,
) -> None:
    """The function copies images provided with filenames from the data_path to the unique_images_path.

    Args:
        filenames (List[str]): A list of filenames of unique images.
        data_path (Union[str, Path]): The data path to the folder for the camera images.
        unique_images_path (str): The path to the folder to copy the unique images to.
    """

    # copy images to keep into data/unique_images/
    for filename in filenames:
        img_path_src: Path = os.path.join(data_path, filename)
        new_filepath = os.path.join(unique_images_path, filename)

        # make sure path exists, there may be multiple folders in the future
        os.makedirs(unique_images_path, exist_ok=True)

        # copy img_path to new filepath
        cmd = ["cp", str(img_path_src), str(new_filepath)]
        # subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(cmd, check=True)


def copy_images_parallel(
    keep_frames: Dict[str, List[str]],
    data_path: Union[str, Path],
    unique_images_path: str = "./data/unique_images",
) -> None:
    """The function is a wrapper to copy images provided with filenames from the data_path \
        to the unique_images_path in parallel.

    Args:
        keep_frames (Dict[str, List[str]]): A dictionary with the camera_id as key and a list of filenames \
            from the images
        data_path (Union[str, Path]): The data path to the folder for the camera images.
        unique_images_path (str, optional): The path to the output folder of the unique images.  \
            Defaults to "./data/unique_images".
    """

    # create folder if not exists
    os.makedirs(unique_images_path, exist_ok=True)

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        # submit a job for each camera ID from the dict to the executor
        futures = [
            executor.submit(copy_images, filenames, data_path, unique_images_path)
            for _, filenames in keep_frames.items()
        ]

        # Wait for for futures completion
        for future in futures:
            future.result()


def compare_images_for_single_camera(
    camera_id: str,
    files: List[str],
    data_path: Union[str, Path],
    gaussian_blur_radius_list: Tuple[int],
    min_contour_area: Union[int, float],
    score_threshold: int = 100,
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """The function compares images for a single camera and returns a dict of images to delete and \
    a dict of images grouped by camera_id to keep.

    Args:
        camera_id (str): The camera id string (i.e. 'c21')
        files (List[str]): A list of image filenames from the camera.
        data_path (Union[str, Path]): The data path to the folder for the camera images.
        gaussian_blur_radius_list (Tuple[int]): A list with radii for gaussian blur to be applied onto the image.
        min_contour_area (Union[int, float]): The min area for contours to be considered.
        score_threshold (int, optional): The score threshold for the comparison. Defaults to 100.

    Raises:
        FileNotFoundError: If an image is not able to be read by cv2.imread() and returns None.

    Returns:
        Tuple[Dict[str, List[str]], Dict[str, List[str]]]: A tuple with two dictionaries. The first dictionary  \
            contains the filenames to delete and the second dictionary contains the filenames to keep grouped by \
                camera id.
    """

    # return dict with camera_ids as keys and filenames are values
    delete_images: Dict[str, List[str]] = dict()
    keep_images: Dict[str, List[str]] = dict()

    prev_frame_same: bool = False

    # iterate over values in files_by_camera_id
    for i in range(len(files) - 1):
        # load image
        prev_frame_path: Path = os.path.join(data_path, files[i])
        next_frame_path: Path = os.path.join(data_path, files[i + 1])

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
        mask: Tuple[int] = (0, 0, 0, 0)  # images should remain unchanged

        # c10 changes size dimensions that are not consistent, which is why no mask is applied
        if camera_id == "c20":
            mask = [0, 29, 0, 0]
        elif camera_id == "c21":
            mask = [0, 30, 0, 0]
        elif camera_id == "c23":
            mask = [0, 32, 0, 0]

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
        score, _, _ = compare_frames_change_detection(
            prev_frame, next_frame, min_contour_area=min_contour_area
        )

        # if score is low enough, delete prev_frame
        if score < score_threshold:
            # add to delete_images
            if camera_id not in delete_images:
                delete_images[camera_id] = []

            delete_images[camera_id].append(files[i])
        else:
            # if the previous frame was already considered to be the same as the next (now), add now to keep_images
            if prev_frame_same:
                if camera_id not in delete_images:
                    delete_images[camera_id] = []
                delete_images[camera_id].append(files[i])
                prev_frame_same = False
                continue

            if camera_id not in keep_images:
                keep_images[camera_id] = []

            keep_images[camera_id].append(files[i])

            prev_frame_same = True

        if i + 1 == len(files):
            if prev_frame_same:
                delete_images[camera_id].append(files[i + 1])
            else:
                keep_images[camera_id].append(files[i + 1])

    logging.info(f"Camera {camera_id} comparison finished.")

    return delete_images, keep_images


def compare_images_parallel(
    files_by_camera_id: Dict[str, List[str]],
    data_path: Union[str, Path],
    gaussian_blur_radius_list: Tuple[int] = (5, 11, 21),
    min_contour_area: Union[int, float] = 500,
    score_threshold: int = 100,
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """The function compares images in parallel for each camera and returns a dict of images to delete and \
    a dict of images grouped by camera_id to keep.

    Args:
        files_by_camera_id (Dict[str, List[str]]): A dictionary with the camera_id as key and a list of filenames \
            from the images.
        data_path (Union[str, Path]): The data path to the folder for the camera images.
        gaussian_blur_radius_list (Tuple[int], optional): A list with radii for gaussian blur  \
            to be applied onto the image. Defaults to (5, 11, 21).
        min_contour_area (Union[int, float], optional): The min area for contours to be considered. Defaults to 500.
        score_threshold (int, optional): The score threshold for the comparison. Defaults to 100.

    Returns:
        Tuple[Dict[str, List[str]], Dict[str, List[str]]]: A tuple with two dictionaries. The first dictionary  \
            contains the filenames to delete and the second dictionary contains the filenames to keep grouped by \
                camera id.
    """

    # return dict with camera_ids as keys and filenames are values
    delete_images: Dict[str, List[str]] = dict()
    keep_images: Dict[str, List[str]] = dict()

    logging.info("Start image comparison for all cameras.")

    # parallelize the comparison of images
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = []
        for camera_id, files in files_by_camera_id.items():
            futures.append(
                executor.submit(
                    compare_images_for_single_camera,
                    camera_id,
                    files,
                    data_path,
                    gaussian_blur_radius_list,
                    min_contour_area,
                    score_threshold,
                )
            )

        for future in futures:
            result_delete, result_keep = future.result()
            delete_images.update(result_delete)
            keep_images.update(result_keep)

    return delete_images, keep_images

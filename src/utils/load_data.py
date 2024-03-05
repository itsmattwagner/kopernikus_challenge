import os
from datetime import datetime  # , timezone TODO REMOVE
from typing import Dict, List


def string_to_date(timestamp_str: str) -> datetime:
    """
    Converts a string to a datetime.date object. The string can either represent
    a unix timestamp (in milliseconds) or a date in the format 'YYYY_MM_DD__HH_MM_SS'.

    Args:
    - timestamp_str (str): The date string to convert.

    Returns:
    - datetime: The converted datetime object.

    Raises:
    - ValueError: If the input string cannot be converted to a datetime object.
    """

    try:
        # Convert the string as a timestamp in milliseconds
        timestamp: float = int(timestamp_str) / 1000
        return datetime.fromtimestamp(timestamp)

    except ValueError:
        try:
            # Convert the string as a custom format date
            return datetime.strptime(timestamp_str, "%Y_%m_%d__%H_%M_%S")
        except ValueError as e:
            # TODO maybe instead of raising error, return None and handle the error in the main function (like skipping the image and logging the error message)
            # Raise error message if both attempts fail
            raise ValueError(
                f"Unable to convert '{timestamp_str}' into a valid date format."
            ) from e


def get_timestamp_from_filename(filename: str) -> str:
    """
    Extracts the timestamp from a filename.

    Args:
    - filename (str): The filename to extract the timestamp from.

    Raises:
    - ValueError: If the input string is empty.

    Returns:
    - str: The timestamp extracted from the filename.
    """

    # check if filename is empty
    if not filename:
        raise ValueError("Filename is empty.")

    # Extract the timestamp from the filename
    return filename[4:].split(".")[0]


def get_images_in_folder(data_path: str) -> Dict[str, List[str]]:
    """
    Returns a dict with filenames (values) sorted by timestamp ascending grouped by camera id (keys).

    Args:
    - data_path (str): The data path to the folder to search for images.

    Returns:
    - Dict[str, List[str]]: A dictionary with the camera_id as key and a list of images from that camera as value.

    Raises:
    - ValueError: If the folder at data_path is empty.
    """

    # Get the list of all files in the folder
    filenames: List[str] = os.listdir(data_path)

    if len(filenames) == 0:
        raise ValueError(f"No images found in the folder '{data_path}'.")

    # dictionary to store images by camera_id
    files_by_camera_id: dict = dict()

    for filename in filenames:
        # store in dictionary with camera_id as key and all images from that camera as value
        camera_id: str = filename[:3]

        # check if camera_id is already in dictionary
        if camera_id not in files_by_camera_id:
            files_by_camera_id[camera_id] = []

        # add the filename to the list of images for the camera_id
        files_by_camera_id[camera_id].append(filename)

    # sort files in files_by_camera by timestamp ascending
    for camera_id in files_by_camera_id:
        files_by_camera_id[camera_id].sort(
            key=lambda filename: string_to_date(get_timestamp_from_filename(filename))
        )

    return files_by_camera_id

#!/usr/bin/env python

import argparse
import errno
import logging
import os
from typing import Dict, List

from src.utils.handle_files import (
    compare_images_parallel,
    copy_images_parallel,
    remove_images,
)
from src.utils.load_data import get_images_in_folder


def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    # check if args.data_path is a valid path
    if not os.path.exists(args.data_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.data_path)

    files_by_camera_id: Dict[str, List[str]] = get_images_in_folder(args.data_path)
    logging.info("Loaded images from %s", args.data_path)

    # call compare_image with files_by_camera_id and args parameters
    delete_frame, keep_frames = compare_images_parallel(
        files_by_camera_id,
        args.data_path,
        args.gaussian_blur_radius_list,
        args.min_contour_area,
        args.score_threshold,
    )
    logging.info("Image comparison for all cameras finished.")

    if args.delete:
        # delete images that are not unique
        remove_images(delete_frame, args.data_path)
        logging.info("Images that are not unique have been deleted.")
    else:
        if args.output_path is None:
            args.output_path = os.path.join(".", "data", "unique_images")
        # copy images to keep into data/unique_images/
        copy_images_parallel(keep_frames, args.data_path, args.output_path)
        logging.info("Images that are unique have been copied to %s", args.output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program removes duplicate images from a dataset.",
        epilog="As an alternative to the commandline, params can be placed in a file, \
            one per line, and specified on the commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars="@",
    )

    parser.add_argument(
        "-v", "--verbose", help="Increase the output verbosity", action="store_true"
    )

    parser.add_argument(
        "--data_path",
        help="Absolute path to the dataset",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--gaussian_blur_radius_list",
        help="A list with radii to be applied onto the image",
        type=int,
        nargs="*",
        required=False,
    )

    parser.add_argument(
        "--min_contour_area",
        help="The min area for contours to be considered",
        type=int,
        required=False,
    )

    parser.add_argument(
        "--score_threshold",
        help="The threshold for the score for two images to be considered similar",
        type=int,
        required=False,
    )

    parser.add_argument(
        "--output_path",
        help="The path to the folder to save the unique images",
        type=str,
        required=False,
    )

    parser.add_argument(
        "--delete",
        help="Determines if the images that are not unique should be deleted. \
            If set, the images will be deleted.  \
            If not set, the images will be copied to the output_path.",
        action="store_true",
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)

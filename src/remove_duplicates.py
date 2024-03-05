#!/usr/bin/env python

import argparse
import errno
import logging
import os
from typing import Dict, List

from src.utils.handle_files import compare_images, copy_images
from src.utils.load_data import get_images_in_folder


def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    # check if args.data_path is a valid path
    if not os.path.exists(args.data_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.data_path)

    files_by_camera_id: Dict[str, List[str]] = get_images_in_folder(args.data_path)

    # call compare_image with files_by_camera_id and args parameters
    delete_frame, keep_frames = compare_images(
        files_by_camera_id,
        args.data_path,
        args.gaussian_blur_radius_list,
        args.min_contour_area,
    )

    # copy images to keep into data/unique_images/
    copy_images(keep_frames, args.data_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Does a thing to some stuff.",
        epilog="As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars="@",
    )

    # TODO add input parameters

    parser.add_argument(
        "-v", "--verbose", help="Increase the output verbosity", action="store_true"
    )

    parser.add_argument(
        "-d",
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

    # TODO add output path for unique images

    args = parser.parse_args()

    # TODO add checks if cli parameters are correct (expected string, but gave integer) or if required parameters are given
    # TODO check if data_path is a valid path

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)

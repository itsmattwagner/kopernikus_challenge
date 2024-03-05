from typing import List, Tuple

import cv2
import imutils
import numpy as np


def draw_color_mask(
    img: np.ndarray,
    borders: List[float | int] | Tuple[float | int],
    color: Tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """The function draws a mask on the image.

    Args:
        img (np.ndarray): An image read from cv2.
        borders (List[float  |  int] | Tuple[float  |  int]): A list of 4 elements representing the percentage of the image to be masked. The order is [x_min, y_min, x_max, y_max].
        color (tuple, optional): Color of the border mask. Defaults to (0, 0, 0).

    Returns:
        np.ndarray: The image with the mask.
    """

    h = img.shape[0]
    w = img.shape[1]

    x_min = int(borders[0] * w / 100)
    x_max = w - int(borders[2] * w / 100)
    y_min = int(borders[1] * h / 100)
    y_max = h - int(borders[3] * h / 100)

    img = cv2.rectangle(img, (0, 0), (x_min, h), color, -1)
    img = cv2.rectangle(img, (0, 0), (w, y_min), color, -1)
    img = cv2.rectangle(img, (x_max, 0), (w, h), color, -1)
    img = cv2.rectangle(img, (0, y_max), (w, h), color, -1)

    return img


def preprocess_image_change_detection(
    img: np.ndarray,
    gaussian_blur_radius_list: List[int] | Tuple[int] = None,
    black_mask: List[float | int] | Tuple[float | int] = (5, 10, 5, 0),
) -> np.ndarray:
    """The function converts the image to grayscale, applies a Gaussian blur, and draws a black mask. The image has to be in the BGR format!

    Args:
        img (np.ndarray): An image read from cv2 in BGR format.
        gaussian_blur_radius_list (List[int] | Tuple[int], optional): A list with radii to be applied onto the image. Defaults to None.
        black_mask (List[float  |  int] | Tuple[float  |  int], optional): A black mask that is drawn onto the image. Defaults to (5, 10, 5, 0).

    Returns:
        np.ndarray: The preprocessed image.
    """

    gray = img.copy()
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    if gaussian_blur_radius_list is not None:
        for radius in gaussian_blur_radius_list:
            gray = cv2.GaussianBlur(gray, (radius, radius), 0)

    gray = draw_color_mask(gray, black_mask)

    return gray


def compare_frames_change_detection(
    prev_frame: np.ndarray, next_frame: np.ndarray, min_contour_area: int | float
) -> Tuple[int, List[float], float]:
    frame_delta = cv2.absdiff(prev_frame, next_frame)
    thresh = cv2.threshold(frame_delta, 45, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    score = 0
    res_cnts = []
    for c in cnts:
        if cv2.contourArea(c) < min_contour_area:
            continue

        res_cnts.append(c)
        score += cv2.contourArea(c)

    return score, res_cnts, thresh

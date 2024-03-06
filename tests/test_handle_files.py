from src.utils.handle_files import copy_images, remove_images


def test_remove_images(mocker):
    """Tests the removal of images from a folder."""

    # create fake os.path.join and subprocess.run
    mocker.patch("os.path.join", return_value="mocked_path")
    mocked_subprocess_run = mocker.patch("subprocess.run")

    # create test data
    delete_images = {"camera1": ["image1.jpg", "image2.jpg"]}
    data_path = "/fake/data_path"

    remove_images(delete_images, data_path)

    assert mocked_subprocess_run.call_count == 2
    mocked_subprocess_run.assert_any_call(["rm", "mocked_path"], check=True)


def test_copy_images(mocker):
    """Tests the copying of images to a new folder."""

    # create fake os.path.join, os.makedirs, and subprocess.run
    mocker.patch("os.path.join", return_value="mocked_path")
    mocker.patch("os.makedirs")
    mocked_subprocess_run = mocker.patch("subprocess.run")

    # create test data
    filenames = ["unique_image1.jpg", "unique_image2.jpg"]
    data_path = "/fake/data_path"
    unique_images_path = "/fake/unique_images_path"

    copy_images(filenames, data_path, unique_images_path)

    # Assertions
    assert mocked_subprocess_run.call_count == len(filenames)
    mocked_subprocess_run.assert_any_call(
        ["cp", "mocked_path", "mocked_path"], check=True
    )

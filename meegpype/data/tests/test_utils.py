import os
from pathlib import Path
from ..utils import get_data_folder


def test_get_data_folder():
    # Call the function to get the data folder path
    data_folder_path = get_data_folder()

    # Check that the returned path is indeed a Path object
    assert isinstance(data_folder_path, Path), "The returned path is not a Path object"

    # Check that the path exists and is a directory
    assert data_folder_path.exists(), "The data folder path does not exist"
    assert data_folder_path.is_dir(), "The data folder path is not a directory"

    # Check that the expected files are in the data directory
    expected_files = os.path.join(
        data_folder_path, "fsLR", "atlas_subparc374.R.32k_fs_LR.label.gii"
    )
    assert os.path.exists(expected_files)

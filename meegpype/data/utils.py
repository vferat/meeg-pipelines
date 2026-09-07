from pathlib import Path


def get_data_folder() -> Path:
    """
    Get the path to the `data` directory in the package.

    Returns
    -------
    Path
        The full path to the `data` directory.
    """
    data_dir = Path(__file__).parent.resolve()
    return data_dir

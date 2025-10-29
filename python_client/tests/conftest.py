import shutil
from pathlib import Path

import pytest


@pytest.fixture
def resources_path() -> Path:
    """
    Get the path of the tests resources directory
    :return: the resources directory path
    """
    return _resources_path()


def copy_resource_file(resource_filename: str, target_dir: Path) -> None:
    """
    Copy a file from the test resources dir to the target directoy
    :param resource_filename: the name of the file within the resources directory
    :param target_dir: the target directory where it should be copied
    """
    shutil.copy(_resources_path() / resource_filename, target_dir)


def _resources_path() -> Path:
    return Path(__file__).parent / "resources"

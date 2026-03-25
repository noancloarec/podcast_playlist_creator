import shutil
from pathlib import Path


def copy_resource_file(resource_filename: str, target_dir: Path) -> None:
    """
    Copy a file from the test resources dir to the target directoy
    :param resource_filename: the name of the file within the resources directory
    :param target_dir: the target directory where it should be copied
    """
    shutil.copy(_resources_path() / resource_filename, target_dir)


def _resources_path() -> Path:
    return Path(__file__).parent / "resources"

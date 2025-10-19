import shutil
from pathlib import Path

import pytest


def copy_resource_file_to(resource_filename: str, target_dir: Path) -> None:
    shutil.copy(Path(__file__).parent / "resources" / resource_filename, target_dir)

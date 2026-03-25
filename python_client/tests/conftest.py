from pathlib import Path

import pytest

from tests.helpers import _resources_path


@pytest.fixture
def resources_path() -> Path:
    """
    Get the path of the tests resources directory
    :return: the resources directory path
    """
    return _resources_path()

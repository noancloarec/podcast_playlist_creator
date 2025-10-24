from os import listdir

import pytest

from conftest import copy_resource_file_to
from python_client.audio_processing import get_duration, convert_to_mp3, cut_audio


def test_convert_to_mp3(tmp_path):
    # Given an input folder containing m4a files
    copy_resource_file_to("sample.m4a", tmp_path)

    # When convert_m4a_files_to_mp3 is executed
    convert_to_mp3(tmp_path / "sample.m4a", tmp_path / "sample.mp3")

    # Then the folder contains both the mp3 and the m4a files
    assert set(listdir(tmp_path)) == {"sample.m4a", "sample.mp3"}


def test_get_duration(resources_path):
    # Given an mp3 file
    file = resources_path / "sample.mp3"

    # Then get_duration can tell the mp3's duration in seconds
    assert get_duration(file) == 5.041633


def test_cut_audio(tmp_path, resources_path):
    # Given an mp3 file
    input_file = resources_path / "sample.mp3"

    # When it is cut from 2 to 4 seconds
    cut_audio(input_file, tmp_path / "sample_2_to_4.mp3", 2, 4)

    # Then the resulting audio file is created and lasts approximately 2 seconds
    assert listdir(tmp_path) == ["sample_2_to_4.mp3"]
    assert get_duration(tmp_path / "sample_2_to_4.mp3") == pytest.approx(2, 0.1)

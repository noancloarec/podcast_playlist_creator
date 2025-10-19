import shutil
from os import listdir
from pathlib import Path

from python_client.audio_processing import convert_m4a_files_to_mp3


def test_convert_m4a_files_to_mp3(tmp_path):
    # Given an input folder containing m4a files
    shutil.copy(Path(__file__).parent / "resources/sample.m4a", tmp_path)

    # When convert_m4a_files_to_mp3 is executed
    convert_m4a_files_to_mp3(tmp_path)

    # Then the folder contains both the mp3 and the m4a files
    assert set(listdir(tmp_path)) == {"sample.m4a", "sample.mp3"}

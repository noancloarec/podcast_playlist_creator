from os import listdir
from pathlib import Path

import eyed3
from pytest_mock import MockerFixture

from conftest import copy_resource_file_to
from python_client.preprocessing import (
    convert_m4a_files_to_mp3,
    set_id3_tags,
    create_dir_if_necessary,
)


def test_convert_m4a_files_to_mp3(tmp_path: Path, mocker: MockerFixture):
    # Given an input folder containing m4a files
    copy_resource_file_to("sample.m4a", tmp_path)

    # When convert_m4a_files_to_mp3 is executed
    convert_m4a_files_to_mp3(tmp_path)

    # Then the folder contains both the mp3 and the m4a files
    assert set(listdir(tmp_path)) == {"sample.m4a", "sample.mp3"}

    # When it is called although the mp3 already exists
    convert_to_mp3_spy = mocker.patch("python_client.upload_podcasts.convert_to_mp3")
    convert_m4a_files_to_mp3(tmp_path)

    # The folder still has this structure but ffmpeg has not been called uselessly
    assert set(listdir(tmp_path)) == {"sample.m4a", "sample.mp3"}
    convert_to_mp3_spy.assert_not_called()


def test_set_id3_tags(tmp_path: Path):
    # Given an input folder that contains an mp3 file which does not have an id3 title set, but has a title info in a separate file rss.xml
    copy_resource_file_to("sample.mp3", tmp_path)
    copy_resource_file_to("rss.xml", tmp_path)

    # When id3 tags are set
    set_id3_tags(tmp_path)

    # Then the file's id3 title is the title provided by rss.xml
    audiofile = eyed3.load(tmp_path / "sample.mp3")
    assert audiofile.tag.title == "Sample file"


def test_create_dir_if_necessary_when_dir_exists(tmp_path: Path):
    # Given an existing directory containing files
    existing_dir = tmp_path / "public"
    existing_dir.mkdir()
    existing_file = existing_dir / "file.txt"
    existing_file.touch()

    # When create_dir_if_necessary creates the directory
    create_dir_if_necessary(existing_dir)

    # Then nothing has changed
    assert str(existing_file.name) in listdir(existing_dir)


def test_create_dir_if_necessary_when_dir_does_not_exist(tmp_path: Path):
    # Given an empty parent directory
    # When create_dir_if_necessary creates the directory
    create_dir_if_necessary(tmp_path / "public")
    # Then the directory has been created
    assert "public" in listdir(tmp_path)

import shutil
from datetime import datetime
from os import listdir
from pathlib import Path

import eyed3
import pytest
from lxml import html
from pytest_mock import MockerFixture

from conftest import copy_resource_file_to
from python_client.feed_xml_processing import XmlFeedSample
from python_client.upload_podcasts import (
    determine_public_dir_path,
    create_dir_if_necessary,
    backup_old_rss_xml_file,
    convert_m4a_files_to_mp3,
    set_id3_tags,
    fill_podcasts_duration,
)


def test_determine_public_dir_path():
    # Given the current folder configuration
    # When python tries to determine the public dir path
    public_dir_path = determine_public_dir_path()
    # The path at the root of the project (i.e. podcast_playlist_creator/public) is returned, i.e. it is next to the python client or the web extension

    assert str(public_dir_path).endswith("/public")
    assert "python_client" in listdir(public_dir_path.parent)


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


def test_backup_old_rss_xml_file_when_file_exists(tmp_path):
    # Given a file rss.xml present in a directory
    (tmp_path / "rss.xml").touch()

    # When it is backed up at a certain time
    backup_old_rss_xml_file(tmp_path, datetime(2025, 10, 30, 8, 12, 0))

    # Then the file is renamed with the given timestamp
    assert listdir(tmp_path) == ["rss_251030_081200.xml"]


def test_backup_old_rss_xml_file_when_file_does_not_exist(tmp_path):
    # Given an empty directory
    # When it is backed up at a certain time
    backup_old_rss_xml_file(tmp_path, datetime(2025, 10, 30, 8, 12, 0))
    # Then the directory still is empty
    assert listdir(tmp_path) == []


def test_convert_m4a_files_to_mp3(tmp_path, mocker: MockerFixture):
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


def test_set_id3_tags(tmp_path):
    # Given an input folder that contains an mp3 file which does not have an id3 title set, but has a title info in a separate file feed.sample.xml
    copy_resource_file_to("sample.mp3", tmp_path)
    copy_resource_file_to("feed.sample.xml", tmp_path)

    # When id3 tags are set
    set_id3_tags(tmp_path)

    # Then the file's id3 title is the title provided by feed.sample.xml
    audiofile = eyed3.load(tmp_path / "sample.mp3")
    assert audiofile.tag.title == "Sample file"


def test_fill_podcasts_duration(tmp_path):
    # Given an input folder with an mp3 and a corresponding feed.sample.xml
    copy_resource_file_to("sample.mp3", tmp_path)
    copy_resource_file_to("feed.sample.xml", tmp_path)

    # When fill_podcast_duration is run
    fill_podcasts_duration(tmp_path)

    # Then the feed.sample.xml files has a duration for this podcast
    feed_sample = XmlFeedSample(tmp_path / "feed.sample.xml")
    feed_sample.set_duration(tmp_path / "sample.mp3", "12")
    feed_sample.save()
    assert feed_sample.get_duration(tmp_path / "sample.mp3") == "00:00:05"

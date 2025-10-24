from datetime import datetime
from os import listdir
from pathlib import Path

from conftest import copy_resource_file_to
from python_client.rss_feed import RssFeed, get_podcast_duration
from python_client.upload_podcasts import (
    determine_public_dir_path,
    create_dir_if_necessary,
    backup_old_rss_xml_file,
    fill_podcasts_duration,
    duration_to_hours,
)


def test_determine_public_dir_path():
    # Given the current folder configuration
    # When python tries to determine the public dir path
    public_dir_path = determine_public_dir_path()
    # The path at the root of the project (i.e. podcast_playlist_creator/public) is returned, i.e. it is next to the python client or the web extension

    assert str(public_dir_path).endswith("/public")
    assert "python_client" in listdir(public_dir_path.parent)


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


def test_fill_podcasts_duration(tmp_path):
    # Given an input folder with an mp3 and a corresponding rss.xml
    copy_resource_file_to("sample.mp3", tmp_path)
    copy_resource_file_to("rss.xml", tmp_path)

    # When fill_podcast_duration is run
    fill_podcasts_duration(tmp_path)

    # Then the rss.xml files has a duration for this podcast
    feed_sample = RssFeed(tmp_path / "rss.xml")
    assert get_podcast_duration(feed_sample, tmp_path / "sample.mp3") == "00:00:05"


def test_duration_to_hours():
    assert duration_to_hours(3600) == "01:00:00"
    assert duration_to_hours(4) == "00:00:04"
    assert duration_to_hours(5.15) == "00:00:05"
    assert duration_to_hours(3727) == "01:02:07"

from os import listdir
from pathlib import Path

import pytest

from conftest import copy_resource_file
from python_client.audio_processing import get_duration
from python_client.split_podcasts import (
    get_segments,
    split_audio,
    get_title_for_each_segment,
    add_title_to_segment,
)


def test_split_audio(tmp_path: Path):
    # Given an mp3 file of 5 secs and a title in an input directory, an empty output directory
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    copy_resource_file("sample.mp3", input_dir)

    # When it is split into parts of 2 secs, with 1 second overlap
    split_audio(
        input_dir / "sample.mp3", output_dir, segment_duration_seconds=2, overlap=1
    )

    # Then it generates 3 parts (seconds 0 to 3, 2 to 5, 4 to 7)
    assert set(listdir(output_dir)) == {
        "sample_part_01_of_03.mp3",
        "sample_part_02_of_03.mp3",
        "sample_part_03_of_03.mp3",
    }
    assert get_duration(output_dir / "sample_part_01_of_03.mp3") == pytest.approx(
        3, 0.1
    )
    assert get_duration(output_dir / "sample_part_02_of_03.mp3") == pytest.approx(
        3, 0.1
    )
    assert get_duration(output_dir / "sample_part_03_of_03.mp3") == pytest.approx(
        1, 0.1
    )


def test_get_segments():
    # Given a duration in seconds, a 2 seconds window with 1 second overlap
    duration = 5.02
    window_size = 2
    overlap = 1

    # When segments are computed
    segments = get_segments(duration, window_size, overlap)

    # Segments have the size duration + overlap, and overlap themselves
    assert segments == [(0, 3), (2, 5), (4, 7)]


def test_get_title_for_each_segment(tmp_path):
    # Given mp3 segments that have been generated, and an rss feed
    segments = [
        tmp_path / "sample_part_01_of_03.mp3",
        tmp_path / "sample_part_02_of_03.mp3",
        tmp_path / "sample_part_03_of_03.mp3",
    ]
    for segment in segments:
        segment.touch()
    copy_resource_file("rss.xml", tmp_path)

    # When get_title_for_each_segment determines what title to give to each segment
    title_by_segment = get_title_for_each_segment(tmp_path / "rss.xml", segments)

    # Then the title from the rss feed is used, prefixed by the episode number
    assert title_by_segment == {
        tmp_path / "sample_part_01_of_03.mp3": "Partie 1 sur 3 de Sample file",
        tmp_path / "sample_part_02_of_03.mp3": "Partie 2 sur 3 de Sample file",
        tmp_path / "sample_part_03_of_03.mp3": "Partie 3 sur 3 de Sample file",
    }


def test_add_title_to_segment(tmp_path):
    # Given an output directory where there is a segment of a certain durationand a title
    copy_resource_file("sample.mp3", tmp_path)
    title = "Partie 2/3 de Episode 5/10 : Le titre"
    duration = get_duration(tmp_path / "sample.mp3")

    # When the title is added at the start
    add_title_to_segment(tmp_path / "sample.mp3", title)

    # Then the mp3 is modified, and lasts longer than before the modification
    assert get_duration(tmp_path / "sample.mp3") > duration

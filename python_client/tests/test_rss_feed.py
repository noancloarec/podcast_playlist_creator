from os import listdir
from pathlib import Path

import pytest

from python_client.rss_feed import (
    get_podcast_title,
    RssFeed,
    set_podcast_duration,
    get_podcast_duration,
    save_rss_feed,
)


@pytest.fixture
def dummy_rss_feed(resources_path) -> RssFeed:
    return RssFeed(resources_path / "rss.xml")


def test_get_podcast_title(dummy_rss_feed: RssFeed):
    assert (
        get_podcast_title(
            dummy_rss_feed,
            Path("/home/user/downloads/Une_journ_e___la_radio_en_mars_1968.mp3"),
        )
        == "Une journée à la radio en mars 1968"
    )


def test_get_duration(dummy_rss_feed: RssFeed):
    assert (
        get_podcast_duration(
            dummy_rss_feed, Path("Une_journ_e___la_radio_en_mars_1968.mp3")
        )
        == "02:00:24"
    )


def test_set_podcast_duration(dummy_rss_feed: RssFeed):
    rss_feed_with_duration = set_podcast_duration(
        dummy_rss_feed, Path("Une_journ_e___la_radio_en_mars_1968.mp3"), "12:09:87"
    )
    assert (
        get_podcast_duration(
            rss_feed_with_duration, Path("Une_journ_e___la_radio_en_mars_1968.mp3")
        )
        == "12:09:87"
    )


def test_save_rss_feed(dummy_rss_feed, tmp_path):
    save_rss_feed(dummy_rss_feed, tmp_path / "dummy.xml")
    assert listdir(tmp_path) == ["dummy.xml"]

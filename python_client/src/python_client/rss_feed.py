from copy import deepcopy
from pathlib import Path

from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, tostring

namespaces = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
for ns, ns_full in namespaces.items():
    ET.register_namespace(ns, ns_full)


class RssFeed:
    def __init__(self, input_file_path: Path):
        content = input_file_path.read_text(encoding="utf-8")
        self.tree = ET.ElementTree(ET.fromstring(content))


def get_podcast_title(rss_feed: RssFeed, podcast_filename: Path) -> str:
    """
    Get the title of a podcast in an RSS feed given the podcast's filename
    :param rss_feed: the rss feed
    :param podcast_filename: the filename of the podcast, only the end of the path will be considered
    :return: the title of the podcast
    """
    return _get_item_title(_get_item(rss_feed, podcast_filename))


def get_podcast_duration(rss_feed: RssFeed, podcast_filename: Path) -> str:
    """
    Get the duration of a podcast in an RSS feed given the podcast's filename
    :param rss_feed: the rss feed
    :param podcast_filename: the filename of the podcast, only the end of the path will be considered
    :return: the duration of the podcast
    """
    print("rss_feed")
    print(tostring(rss_feed.tree.getroot()))
    item = _get_item(rss_feed, podcast_filename)
    duration_element: Element | None = item.find(
        "itunes:duration", namespaces=namespaces
    )

    # Sometimes Elementtree does not accept the namespaces
    if duration_element is None:
        duration_element = item.find("itunes:duration")

    if duration_element is None:
        raise IndexError(f"Could not find duration in {tostring(item)}")

    return duration_element.text


def set_podcast_duration(
    rss_feed: RssFeed, podcast_filename: Path, duration: str
) -> RssFeed:
    """
    Set the duration of a podcast in an RSS feed given the podcast's filename, returning a new RSS Feed
    :param rss_feed: the rss feed
    :param podcast_filename: the filename of the podcast, only the end of the path will be considered
    :param duration: The duration of the podcast
    :return: The RSSFeed with the duration item modified
    """
    rss_feed = deepcopy(rss_feed)
    item = _get_item(rss_feed, podcast_filename)
    duration_element: Element | None = item.find(
        "itunes:duration", namespaces=namespaces
    )
    item.remove(duration_element)
    duration_element = Element("itunes:duration")
    duration_element.text = duration
    item.append(duration_element)
    return rss_feed


def save_rss_feed(rss_feed: RssFeed, path: Path) -> None:
    rss_feed.tree.write(path, encoding="utf-8")


def _get_item(rss_feed: RssFeed, podcast_filename: Path) -> Element:
    try:
        return next(
            item
            for item in rss_feed.tree.find("channel").findall("item")
            if _get_item_filename(item) == podcast_filename.name
        )
    except StopIteration:
        print(
            f"Cannot find the podcast {podcast_filename.name} in this list of items : {[ET.tostring(item) for item in rss_feed.tree.find("channel").findall("item")]}"
        )
        raise


def _get_item_title(item: Element) -> str:
    title_tag: Element = item.find("title")
    return title_tag.text


def _get_item_filename(item: Element) -> str:
    url: str = item.find("enclosure").attrib["url"]
    filename = url.split("/")[-1]
    return filename

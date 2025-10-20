from pathlib import Path
from textwrap import dedent

from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, ParseError


class XmlFeedSample:

    namespaces = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}

    for ns, ns_full in namespaces.items():
        ET.register_namespace(ns, ns_full)

    def __init__(self, input_file_path: Path):
        content = input_file_path.read_text(encoding="utf-8")
        try:
            self.tree = ET.ElementTree(ET.fromstring(content))
        except ParseError:
            self.tree = ET.ElementTree(
                ET.fromstring(
                    (
                        dedent(
                            """\
            <rss version=\"2.0\" xmlns:itunes=\"http://www.itunes.com/dtds/podcast-1.0.dtd\">
                <script />
                <channel>
                    <title>Noan's podcasts</title>
                    <link>https://podcasts-noan.web.app/rss.xml</link>
                    <description>An auto generated podcast playlist</description>
                    <language>fr</language>
                    <copyright>Radio France, Timeline</copyright>"""
                        )
                        + input_file_path.read_text(encoding="utf-8")
                        + dedent(
                            """\
                </channel>
            </rss>"""
                        )
                    )
                )
            )

        self.path = input_file_path

    def save(self):
        self.tree.write(self.path, encoding="utf-8")

    def get_podcast_title(self, podcast_filename: Path) -> str:
        return get_item_title(self._get_corresponding_item(podcast_filename))

    def get_duration(self, podcast_filename: Path) -> str:
        item = self._get_corresponding_item(podcast_filename)
        duration_element: Element | None = item.find(
            "itunes:duration", namespaces=self.namespaces
        )
        return duration_element.text

    def set_duration(self, podcast_filename: Path, duration: str):
        item = self._get_corresponding_item(podcast_filename)
        duration_element: Element | None = item.find(
            "itunes:duration", namespaces=self.namespaces
        )

        item.remove(duration_element)
        duration_element = Element("itunes:duration")
        duration_element.text = duration
        item.append(duration_element)

    def _get_corresponding_item(self, podcast_filename: Path) -> Element:
        try:
            return next(
                item
                for item in self.tree.find("channel").findall("item")
                if get_item_filename(item) == podcast_filename.name
            )
        except StopIteration:
            print(
                f"Cannot find the podcast {podcast_filename.name} in this list of items : {list(self.tree.find("channel").findall("item"))}"
            )
            raise


def get_item_title(item: Element) -> str:
    title_tag: Element = item.find("title")
    return title_tag.text


def get_item_filename(item: Element) -> str:
    url: str = item.find("enclosure").attrib["url"]
    filename = url.split("/")[-1]
    return filename

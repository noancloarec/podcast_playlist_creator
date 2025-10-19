from pathlib import Path

from lxml import etree
from lxml.html import HtmlElement, fromstring


class XmlFeedSample:

    def __init__(self, input_file_path: Path):
        self.html: HtmlElement = fromstring(input_file_path.read_text(encoding="utf-8"))
        self.path = input_file_path

    def save(self):
        content: bytes = etree.tostring(self.html, encoding="utf-8")
        Path(self.path).write_text(content.decode(encoding="utf-8"), encoding="utf-8")

    def get_podcast_title(self, podcast_filename: Path) -> str:
        return get_item_title(self._get_corresponding_item(podcast_filename))

    def get_duration(self, podcast_filename: Path) -> str:
        item = self._get_corresponding_item(podcast_filename)
        duration_element: HtmlElement | None = next(
            child for child in item if child.tag == "itunes:duration"
        )
        return duration_element.text_content()

    def set_duration(self, podcast_filename: Path, duration: str):
        item = self._get_corresponding_item(podcast_filename)
        duration_element: HtmlElement | None = next(
            child for child in item if child.tag == "itunes:duration"
        )
        item.remove(duration_element)
        item.append(fromstring(f"<itunes:duration>{duration}</itunes:duration>"))

    def _get_corresponding_item(self, podcast_filename: Path) -> HtmlElement:
        return next(
            item
            for item in self.html
            if get_item_filename(item) == podcast_filename.name
        )


def get_item_title(item: HtmlElement) -> str:
    title_tag: HtmlElement = next(child for child in item if child.tag == "title")
    return title_tag.text


def get_item_filename(item: HtmlElement) -> str:
    enclosure_tag: HtmlElement = next(
        child for child in item if child.tag == "enclosure"
    )
    url: str = enclosure_tag.attrib["url"]
    filename = url.split("/")[-1]
    return filename

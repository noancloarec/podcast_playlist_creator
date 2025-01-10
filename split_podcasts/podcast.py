from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup


@dataclass
class Podcast:
    filename:str
    title: str

def get_podcasts(sample_xml:Path)->list[Podcast]:
    """
    Read the sample xml file to return info about podcasts
    :param sample_xml: path to the xml file
    :return: the podcasts in the sample xml
    """
    with open(sample_xml, "r") as fp:
        soup = BeautifulSoup(fp, "html.parser")

    return [
        Podcast(
            title= item.find_next("title").text,
            filename = Path(item.find_next("enclosure")["url"]).name
        )
        for item in soup.find_all("item")
    ]



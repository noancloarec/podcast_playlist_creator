from pathlib import Path

import eyed3
from tqdm import tqdm

from python_client.rss_feed import (
    RssFeed,
    get_podcast_title,
)


def get_mp3_files(folder: Path) -> list[Path]:
    """
    List all mp3 files in a directory
    :param folder: the directory
    :return: the path of all mp3 files
    """
    return [filename for filename in folder.iterdir() if filename.suffix == ".mp3"]


def set_id3_tags(in_directory: Path) -> None:
    """
    Take the rss.xml file in a directory, use the title of each item in the rss feed to set the mp3's title metadata
    :param in_directory:
    :return:
    """
    eyed3.log.setLevel("ERROR")
    rss_feed = RssFeed(in_directory / "rss.xml")

    for mp3_file in tqdm(get_mp3_files(in_directory), "Setting id3 tags"):
        audio_file = eyed3.load(mp3_file)
        audio_file.tag.title = get_podcast_title(rss_feed, mp3_file)
        audio_file.tag.save()

    return None


def convert_m4a_files_to_mp3(in_directory: Path) -> None:
    """
    Convert all m4a files in a directory into mp3 files using ffmpeg
    Skips m4a which already have an equivalent mp3 in the directory
    :param in_directory: directory that contains mp3s
    """
    files = list(in_directory.iterdir())
    m4a_to_convert = [
        filename
        for filename in files
        if filename.suffix == ".m4a" and filename.with_suffix(".mp3") not in files
    ]
    if not len(m4a_to_convert):
        print("No m4a to convert")
        return
    for m4a_file in tqdm(m4a_to_convert, "Converting m4a files to mp3"):
        print(m4a_file)


def create_dir_if_necessary(dir_path: Path) -> None:
    """
    Create a directory only if it does not exist yet
    Used to create the public directory which will store podcasts
    :param dir_path: the directory's path
    """
    dir_path.mkdir(exist_ok=True)

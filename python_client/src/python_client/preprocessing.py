from pathlib import Path

import eyed3
from tqdm import tqdm

from python_client.audio_processing import convert_to_mp3
from python_client.rss_feed import (
    RssFeed,
    get_podcast_title,
    list_filenames,
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
    :param in_directory: The directory containing an rss.xml file and the mp3 files mentioned in the rss.xml
    """
    eyed3.log.setLevel("ERROR")
    rss_feed = RssFeed(in_directory / "rss.xml")

    for mp3_file in tqdm(get_mp3_files(in_directory), "Setting id3 tags"):
        audio_file = eyed3.load(mp3_file)
        if audio_file is None:
            raise ValueError(
                f"EyeD3 could not read the file {mp3_file}, you may retry the download if the file is corrupt, or remove it."
            )
        audio_file.tag.title = get_podcast_title(rss_feed, mp3_file)
        audio_file.tag.save(encoding="utf-8")


def convert_m4a_files_to_mp3(in_directory: Path) -> None:
    """
    Convert all m4a files in a directory into mp3 files using ffmpeg
    Skips m4a which already have an equivalent mp3 in the directory
    :param in_directory: directory that contains mp3s
    """
    files = list(in_directory.iterdir())
    m4as_to_convert = [
        filename
        for filename in files
        if filename.suffix == ".m4a" and filename.with_suffix(".mp3") not in files
    ]
    if not len(m4as_to_convert):
        print("No m4a to convert")
        return
    for m4a_file in tqdm(m4as_to_convert, "Converting m4a files to mp3"):
        convert_to_mp3(m4a_file, m4a_file.with_suffix(".mp3"))


def create_dir_if_necessary(dir_path: Path) -> None:
    """
    Create a directory only if it does not exist yet
    Used to create the public directory which will store podcasts
    :param dir_path: the directory's path
    """
    dir_path.mkdir(exist_ok=True)


def ensure_no_unnecessary_files_will_be_uploaded(input_path: Path) -> None:
    """
    Make sure there are no unnecessary file to be uploaded
    This is relevant so the user remember to clean its download directory from all the previous podcast they have already listened to and do not need to be uploaded again.
    :param input_path: The input directory that contains the podcasts and the rss.xml file
    """
    rss_feed = RssFeed(input_path / "rss.xml")
    filenames_in_feed = set(Path(f).stem for f in list_filenames(rss_feed))
    unneccessary_filenames_in_input_directory = [
        filename
        for filename in input_path.iterdir()
        if filename.stem not in filenames_in_feed and filename.suffix != ".xml"
    ]
    if unneccessary_filenames_in_input_directory:
        filenames_list = "\n".join(
            filename.name for filename in unneccessary_filenames_in_input_directory
        )
        raise ValueError(
            (
                f"The following files are present in the directory {input_path} "
                "but are not found in the file rss.xml: \n"
                f"{filenames_list}"
            )
        )

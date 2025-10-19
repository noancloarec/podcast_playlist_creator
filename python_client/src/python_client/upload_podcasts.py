import sys
from datetime import datetime
from pathlib import Path

import eyed3

from python_client.audio_processing import convert_to_mp3, get_duration
from python_client.feed_xml_processing import (
    get_item_filename,
    get_item_title,
    XmlFeedSample,
)


def upload_podcasts():
    input_folder = Path(sys.argv[1])

    public_dir_path = determine_public_dir_path()
    create_dir_if_necessary(public_dir_path)
    backup_old_rss_xml_file(public_dir_path, datetime.now())
    convert_m4a_files_to_mp3(input_folder)
    set_id3_tags(input_folder)
    fill_podcasts_duration(input_folder)
    pass


def get_mp3_files(folder: Path) -> list[Path]:
    return [filename for filename in folder.iterdir() if filename.suffix == ".mp3"]


def duration_to_hours(duration_in_seconds: float) -> str:
    duration_in_seconds = int(duration_in_seconds)
    hours = duration_in_seconds // 3600
    minutes = (duration_in_seconds - 3600 * hours) // 60
    seconds = duration_in_seconds % 60 // 1
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def fill_podcasts_duration(in_directory: Path) -> None:
    xml_feed = XmlFeedSample(in_directory / "feed.sample.xml")
    for mp3_file in get_mp3_files(in_directory):
        duration = get_duration(mp3_file)
        xml_feed.set_duration(mp3_file, duration_to_hours(duration))
    xml_feed.save()


def set_id3_tags(in_directory: Path) -> None:
    xml_feed = XmlFeedSample(in_directory / "feed.sample.xml")

    for mp3_file in get_mp3_files(in_directory):
        audio_file = eyed3.load(mp3_file)
        audio_file.tag.title = xml_feed.get_podcast_title(mp3_file)
        audio_file.tag.save()

    return None


def convert_m4a_files_to_mp3(in_directory: Path) -> None:
    files = list(in_directory.iterdir())
    for filename in files:
        if filename.suffix == ".m4a" and filename.with_suffix(".mp3") not in files:
            convert_to_mp3(filename, filename.with_suffix(".mp3"))


def backup_old_rss_xml_file(public_dir_path: Path, timestamp: datetime) -> None:
    """ "
    Back up the rss file, if it exists, by adding a timestamp to its name
    :param public_dir_path the path of the public
    :param timestamp the timestamp used to rename the file
    """
    suffix = timestamp.strftime("%y%m%d_%H%M%S")
    try:
        (public_dir_path / "rss.xml").rename(public_dir_path / f"rss_{suffix}.xml")
    except FileNotFoundError:
        pass


def create_dir_if_necessary(dir_path: Path) -> None:
    """
    Create a directory only if it does not exist yet
    Used to create the public directory which will store podcasts
    :param dir_path: the directory's path
    """
    dir_path.mkdir(exist_ok=True)


def determine_public_dir_path() -> Path:
    """
    Determine the path of the public directory
    I.e. the directory that should contain the podcast and rss file, this directory will be uploaded to the web
    :return:
    """
    return Path(__file__).parents[3] / "public"

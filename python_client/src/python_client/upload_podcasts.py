import shutil
import sys
from datetime import datetime
from pathlib import Path

from python_client.audio_processing import get_duration
from python_client.firebase_hosting import create_firebase_json
from python_client.preprocessing import (
    convert_m4a_files_to_mp3,
    set_id3_tags,
    get_mp3_files,
)
from python_client.rss_feed import (
    RssFeed,
    save_rss_feed,
    set_podcast_duration,
)


def upload_podcasts():

    input_folder = Path(sys.argv[1])

    public_dir_path = determine_public_dir_path()
    create_dir_if_necessary(public_dir_path)
    backup_old_rss_xml_file(public_dir_path, datetime.now())
    convert_m4a_files_to_mp3(input_folder)
    set_id3_tags(input_folder)
    fill_podcasts_duration(input_folder)

    shutil.copy(input_folder / "rss.xml", public_dir_path / "rss.xml")
    for mp3_file in get_mp3_files(input_folder):
        shutil.copy(mp3_file, public_dir_path / mp3_file.name)
    create_firebase_json(public_dir_path)


def duration_to_hours(duration_in_seconds: float) -> str:
    """
    Translate a duration in seconds into a string representation of a duration to hours
    e.g. 3601 becomes 01:00:01
    :param duration_in_seconds: the duration in seconds
    :return: the equivalent in hours:minutes:seconds, as string
    """
    duration_in_seconds = int(duration_in_seconds)
    hours = duration_in_seconds // 3600
    minutes = (duration_in_seconds - 3600 * hours) // 60
    seconds = duration_in_seconds % 60 // 1
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def fill_podcasts_duration(in_directory: Path) -> None:
    """
    Given a directory that contains mp3s and an rss feed, modifies the duration item in the rss feed after having determined it with ffmpeg
    :param in_directory: the directory that contains mp3s and an rss feed
    """
    xml_feed = RssFeed(in_directory / "rss.xml")
    for mp3_file in get_mp3_files(in_directory):
        duration = get_duration(mp3_file)
        xml_feed = set_podcast_duration(xml_feed, mp3_file, duration_to_hours(duration))
    save_rss_feed(xml_feed, in_directory / "rss.xml")


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


def determine_public_dir_path() -> Path:
    """
    Determine the path of the public directory
    I.e. the directory that should contain the podcast and rss file, this directory will be uploaded to the web
    :return:
    """
    return Path(__file__).parents[3] / "public"


if __name__ == "__main__":
    upload_podcasts()

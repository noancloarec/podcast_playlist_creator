import shutil
from argparse import Namespace, ArgumentParser
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory

from tqdm import tqdm

from python_client.audio_processing import get_duration, cut_audio, concatenate_mp3s
from python_client.preprocessing import get_mp3_files
from python_client.rss_feed import RssFeed, get_podcast_title
from python_client.text_to_speech import generate_part_title_audio
from python_client.upload_podcasts import convert_m4a_files_to_mp3


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Simple calculator")
    parser.add_argument(
        "input_folder",
        type=str,
        help="Input folder where audio files and feed.sample.xml files are downloaded",
    )
    parser.add_argument("output_folder", type=str, help="Output folder")
    return parser.parse_args()


def split_podcasts():
    args = parse_args()
    input_dir = Path(args.input_folder)
    output_dir = Path(args.output_folder)
    output_dir.mkdir(exist_ok=True)

    convert_m4a_files_to_mp3(input_dir)

    for mp3_file in tqdm(get_mp3_files(input_dir), "Cutting podcasts"):
        split_audio(mp3_file, output_dir, segment_duration_seconds=600, overlap=10)

    for segment, title in tqdm(
        get_title_for_each_segment(
            input_dir / "rss.xml", get_mp3_files(output_dir)
        ).items(),
        desc="Adding title to audio files",
    ):
        add_title_to_segment(segment, title)


def add_title_to_segment(segment: Path, title: str) -> None:
    """
    Modify the mp3 segment at the given path to add a voice saying the title at the beginning of the audio
    :param segment: mp3 segment to modify
    :param title: audio to add
    """
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        title_audio_filename = tmp_dir / f"title.mp3"
        generate_part_title_audio(title, title_audio_filename)
        title_and_segment_mp3 = tmp_dir / "title_and_segment.mp3"
        concatenate_mp3s([title_audio_filename, segment], title_and_segment_mp3)
        shutil.copy(title_and_segment_mp3, segment)


# def split_podcast_and_add_title_at_start(
#     podcast: Podcast,
#     input_dir: Path,
#     output_dir: Path,
#     part_duration: int,
#     overlap: int,
# ) -> None:
#     """
#     Split the podcast in several parts of a given duration, add the title pronounced at the beginning of each podcast
#     :param podcast: the podcast to be splat
#     :param input_dir: the dir where the podcast can be found
#     :param output_dir: the dir where to write the podcast parts
#     """
#     podcast_stem = str(Path(podcast.filename).stem)
#     with TemporaryDirectory() as temp_dir_str:
#         temp_dir = Path(temp_dir_str)
#
#         for part_number, total_parts, part_filename in split_audio(
#             input_dir / podcast.filename, temp_dir, part_duration
#         ):
#             title_audio = temp_dir / (
#                 podcast_stem + f"_partie_{part_number:02}_title.mp3"
#             )
#
#             generate_part_title_audio(
#                 f"Partie {part_number}/{total_parts} de {podcast.title}",
#                 title_audio,
#             )
#
#             merge_mp3s(
#                 title_audio,
#                 part_filename,
#                 output_dir / part_filename.name,
#             )


def get_segments(
    duration: float, window_size: int, overlap: int
) -> list[tuple[int, int]]:
    """
    Generates the segments of an audio to be split into windows with an overlap
    :param duration:
    :param window_size:
    :param overlap:
    :return:
    """
    return [
        (timecode, timecode + window_size + overlap)
        for timecode in range(0, ceil(duration), window_size)
    ]


def split_audio(
    input_file: Path, output_dir: Path, segment_duration_seconds: int, overlap: int
) -> None:
    """
    split an audio file into parts of an approximate duration
    :param input_file: The file to split
    :param output_dir: The target directory for the splits
    :param segment_duration_seconds: the approximate duration of a split in seconds
    :param overlap: The overlap between each segments, so a sentence is not cut in the middle
    :return: An iterator of tuples (part_number, total_parts, duration)
    """
    duration = get_duration(input_file)
    segments = get_segments(duration, segment_duration_seconds, overlap)
    for part_number, (lower_bound, upper_bound) in tqdm(
        enumerate(segments), total=len(segments), desc=f"Cutting {input_file.name}"
    ):
        filename_suffix = f"_part_{part_number+1:02d}_of_{len(segments):02d}.mp3"
        cut_audio(
            input_file,
            output_file=output_dir / (input_file.stem + filename_suffix),
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )


def get_title_for_each_segment(rss_file: Path, segments: list[Path]) -> dict[Path, str]:
    """
    Generate the title to give to each segment, relying on the segment filename and the rss feed info
    :param rss_file: the rss feed
    :param segments: the segments
    :return A dictionary of segments and corresponding title
    """
    rss_feed = RssFeed(rss_file)
    return {segment: _get_title_for_segment(rss_feed, segment) for segment in segments}


def _get_title_for_segment(rss_feed: RssFeed, segment: Path) -> str:
    """
    Generate the title to give to a segment, relying on the segment filename and the rss feed info
    :param rss_feed: the rss feed
    :param segment: the segment
    :return the appropriate title for the segment
    """

    path_in_rss_feed = Path(segment.stem[:-14] + ".mp3")
    title = get_podcast_title(rss_feed, path_in_rss_feed)
    segment_number = int(segment.stem[-8:-6])
    total_segments = int(segment.stem[-2:])
    return f"Partie {segment_number} sur {total_segments} de {title}"

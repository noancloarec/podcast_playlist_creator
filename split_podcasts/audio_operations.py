from math import ceil
from pathlib import Path
from typing import Iterator

import ffmpeg


def convert_to_mp3(input_file: Path, output_file: Path) -> None:
    """
    Converts an audio file to mp3
    :param input_file: path of the input file
    :param output_file: path of the output file
    """
    ffmpeg.input(str(input_file)).output(
        str(output_file),
        acodec="libmp3lame",  # Specify MP3 codec
        ac=2,  # Set audio channels to 2
        ab="192k",  # Set audio bitrate to 192k
        y=None,  # Overwrite output files without asking
    ).global_args("-v", "5").run()


def merge_mp3s(title_mp3: Path, content_mp3: Path, output_mp3: Path) -> None:
    """
    Concatenate 2 mp3 files using ffmpeg, reencode the audio (here the title of the part and its content)
    :param title_mp3: The path to the title
    :param content_mp3: The path to the content
    :param output_mp3 : The output file pat
    """
    ffmpeg.input(f"concat:{title_mp3}|{content_mp3}").output(
        str(output_mp3), acodec="libmp3lame"
    ).run(overwrite_output=True)


def split_audio(
    input_file: Path, output_dir, segment_duration_seconds
) -> Iterator[tuple[int, int, Path]]:
    """
    split an audio file into parts of an approximate duration
    :param input_file: The file to split
    :param output_dir: The target directory for the splits
    :param segment_duration_seconds: the approximate duration of a split in seconds
    :return: An iterator of tuples (part_number, total_parts, duration)
    """
    duration = float(ffmpeg.probe(input_file)["format"]["duration"])
    # The next part will start 10 seconds before the end of the previous part, so the listener can better understand the splat sentence
    overlap = 10
    cuts = range(0, ceil(duration), segment_duration_seconds)
    for index, threshold in enumerate(cuts):
        part_number = index + 1
        output_file = Path(output_dir) / (
            str(input_file.stem) + f"_partie_{part_number}.mp3"
        )

        ffmpeg.input(str(input_file), ss=threshold).output(
            str(output_file), t=segment_duration_seconds + overlap
        ).run(overwrite_output=True)
        yield part_number, len(cuts), output_file

from pathlib import Path

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
        loglevel="quiet",
    ).global_args("-v", "5").run()


def get_duration(input_file: Path) -> float:
    return float(ffmpeg.probe(input_file)["format"]["duration"])


def cut_audio(
    input_file: Path, output_file: Path, lower_bound: float, upper_bound: float
) -> None:
    """
    Cut a part of an audio file
    :param input_file: the input file path
    :param output_file: the output file path
    :param lower_bound: start of the segment to cut
    :param upper_bound: end of the segment to cut
    """
    if not input_file.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    if not output_file.parent.exists():
        raise FileNotFoundError(f"Folder not found: {input_file}")
    ffmpeg.input(str(input_file), ss=lower_bound).output(
        str(output_file), t=upper_bound - lower_bound, loglevel="quiet"
    ).run(overwrite_output=True)


def concatenate_mp3s(mp3s: list[Path], output_mp3: Path) -> None:
    """
    Concatenate 2 mp3 files using ffmpeg, reencode the audio (here the title of the part and its content)
    :param first_mp3: The path to the title
    :param second_mp3: The path to the content
    :param output_mp3 : The output file pat
    """
    ffmpeg_argument = "|".join(str(mp3) for mp3 in mp3s)
    ffmpeg.input(f"concat:{ffmpeg_argument}").output(
        str(output_mp3), acodec="libmp3lame", loglevel="quiet"
    ).run(overwrite_output=True)

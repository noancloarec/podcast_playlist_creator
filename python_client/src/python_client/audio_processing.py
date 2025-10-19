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
    ).global_args("-v", "5").run()

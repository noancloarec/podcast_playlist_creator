from pathlib import Path


_tts = None

def make_title_pronounceable(title: str) -> str:
    """
    Replaces some string in a title to make it pronounceable by coqui
    :param title: the title to be made pronounceable
    :return: the title usable by TTS
    """
    return (
        title.replace("/", " sur ")
        .replace("11", "onze")
        .replace("10", "dix")
        .replace("9", "neuf")
        .replace("8", "huit")
        .replace("7", "sept")
        .replace("6", "six")
        .replace("5", "cinq")
        .replace("4", "quatre")
        .replace("3", "trois")
        .replace("2", "deux")
        .replace("1", "un")
    )


def get_tts():
    """
    A singleton for the tts API containing the import because it is very slow
    :return:
    """
    global _tts
    if _tts is None:
        # Import here after arguments validation because the import is slow
        from TTS.api import TTS

        _tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    return _tts

def generate_part_title_audio(title: str, output_filename: Path):
    title_to_tell = make_title_pronounceable(title)
    filename_wav = output_filename.with_suffix(".wav")
    get_tts().tts_to_file(
        text=title_to_tell,
        file_path=str(filename_wav),
        language="fr",
        speaker="Eugenio Mataracı",
        speed=2.0,
    )
    convert_to_mp3(filename_wav, output_filename)

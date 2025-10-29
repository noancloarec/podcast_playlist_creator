from pathlib import Path

from picotts import PicoTTS

from python_client.audio_processing import convert_to_mp3


def generate_part_title_audio(title: str, output_filename: Path) -> None:
    """
    Create an audio file of a voice saying the given title
    :param title: title to say
    :param output_filename: target audio file
    """
    title_to_tell = _make_title_pronounceable(title)
    filename_wav = output_filename.with_suffix(".wav")
    picotts = PicoTTS()
    picotts.voice = "fr-FR"
    wavs = picotts.synth_wav(title_to_tell)
    with open(filename_wav, "wb") as buffer:
        buffer.write(wavs)
    convert_to_mp3(filename_wav, output_filename)
    filename_wav.unlink()


def _make_title_pronounceable(title: str) -> str:
    """
    Replaces some string in a title to make it pronounceable by coqui
    :param title: the title to be made pronounceable
    :return: the title usable by TTS
    """
    return title.replace("/", " sur ")

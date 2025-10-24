from os import listdir

from python_client.text_to_speech import (
    make_title_pronounceable,
    generate_part_title_audio,
)


def test_make_title_pronounceable():
    assert make_title_pronounceable("Episode 1/12") == "Episode 1 sur 12"


def test_generate_part_title_audio(tmp_path):
    # Given an output filename and a title
    output_file = tmp_path / "coucou.mp3"
    title = "Episode 1 sur 10"

    # When the audio title is generated
    generate_part_title_audio(title, output_file)

    # Then an audio file is generated
    assert listdir(tmp_path) == ["coucou.mp3"]

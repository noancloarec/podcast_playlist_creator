from json import dump
from pathlib import Path


def create_firebase_json(public_dir: Path) -> None:
    """
    Create a file firebase.json in the current directory containing the path of the public directory
    :param public_dir: where the public dir is, i.e. the directory containing the podcasts to upload
    """
    json_content = {"hosting": {"public": str(public_dir)}}
    with open("firebase.json", "w", encoding="utf-8") as f:
        dump(json_content, f)

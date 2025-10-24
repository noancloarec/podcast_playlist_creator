from json import dump
from pathlib import Path


def create_firebase_json(public_dir: Path) -> None:
    json_content = {"hosting": {"public": str(public_dir)}}
    with open("firebase.json", "w", encoding="utf-8") as f:
        dump(json_content, f)

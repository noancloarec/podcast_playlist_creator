import os
from json import load
from pathlib import Path

from python_client.firebase_hosting import create_firebase_json


def test_create_firebase_json(tmp_path):
    # Given a current directory and public dir path
    os.chdir(tmp_path)
    public_dir = Path("/home/the/public/directory")

    # When create_firebase_json is called
    create_firebase_json(public_dir)

    # Then a firebase.json file is created in the current directory and it has a hosting.public section set to the provided path
    with open(tmp_path / "firebase.json", "r", encoding="utf-8") as f:
        firebase_config = load(f)

    assert firebase_config["hosting"]["public"] == str(public_dir)

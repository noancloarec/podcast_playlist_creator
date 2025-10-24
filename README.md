# podcast_playlist_creator

Create an RSS feed usable by playrun

## Installation instruction
### Prerequisites
 - python
 - poetry

## Installation steps
```shell
sudo apt-get install libttspico-utils ffmpeg
cd python_client
poetry install
```

## Usage
### Publish the podcast on your firebase project
After having downloaded the podcast into your `$HOME/podcast_creator`
```shell
python -m python_client
```
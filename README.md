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
./upload-podcasts.sh $HOME/podcast_creator
```

### Split the podcasts you have downloaded
This is useful for devices that do not have a fast-forward or backward functionnality. To avoid having to listen to the entire podcast when only interested in the second half of it.  
This was made to be able to listen to podcasts with my swimming headset, which does not have a screen to display what track is being read.
```shell
cd python_client
./split_podcasts.sh $HOME/Downloads/podcasts_to_split $HOME/Downloads/split_podcasts
``` 
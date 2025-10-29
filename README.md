# podcast_playlist_creator

Create an RSS feed usable by playrun

## Installation
### Prerequisites
 - python
 - poetry

### Install the web extension
From [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/podcast-playlist-creator/).  
Or for development purposes, add the `extension/manifest.json` from the `about:debugging` tab
### Install the python client
Once the podcasts are downloaded with the extension
```shell
sudo apt-get install libttspico-utils ffmpeg
cd python_client
poetry install
```

## Usage
### The extension
The extension will catch the podcasts you start in the browser, and allow to download the corresponding audio files and an RSS feed
### Publish the podcast on your firebase project
After having downloaded the podcast into your `$HOME/podcast_creator`
```shell
./upload-podcasts.sh $HOME/podcast_creator
```
Then the RSS feed will be usable by a podcast app.

### Split the podcasts you have downloaded
This is useful for devices that do not have a fast-forward or backward functionnality. To avoid having to listen to the entire podcast when only interested in the second half of it.  
This was made to be able to listen to podcasts with my swimming headset, which does not have a screen to display what track is being read.
```shell
cd python_client
./split_podcasts.sh $HOME/Downloads/podcasts_to_split $HOME/Downloads/split_podcasts
``` 
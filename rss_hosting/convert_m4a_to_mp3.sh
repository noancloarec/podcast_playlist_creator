#!/bin/bash
media_dir=$1
for filename in $1/*; do
  extension="${filename##*.}"
  if [[ $extension == "m4a" ]]; then
    filename_without_extension="${filename%.*}"
    filename_mp3=$filename_without_extension.mp3
    if [ ! -f $filename_mp3 ]; then
      echo "Converting $filename to mp3, this may take some time."
      ffmpeg -v 5 -y -i $filename -acodec libmp3lame -ac 2 -ab 192k $filename_mp3
    fi
  fi
done
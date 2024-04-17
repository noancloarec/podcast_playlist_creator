#!/bin/bash
IFS=''

while read p || [ -n "$p" ]; do
if [[ $p == *"url="* ]]; then
  filename=$(echo $p | cut -d '"' -f 2 | cut -d '/' -f 4)
  duration=$(ffmpeg -i $1/$filename 2>&1 | grep Duration | cut -d '.' -f 1 | cut -d ' ' -f 4)
fi
if [[ $p == *"itunes:duration"* ]]; then
    echo "        <itunes:duration>$duration</itunes:duration>"
else
    echo $p
fi
done < $1/feed.sample.xml

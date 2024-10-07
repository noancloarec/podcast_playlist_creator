#!/bin/bash
IFS=''

while read p || [ -n "$p" ]; do
if [[ $p == *"<title>"* ]]; then
  title=$(echo $p | cut -d '>' -f 2 | cut -d '<' -f 1)
fi
if [[ $p == *"url="* ]]; then
  filename=$(echo $p | cut -d '"' -f 2 | cut -d '/' -f 4)
fi
if [[ $p == *"</item>"* ]]; then
    eyeD3 --quiet -t "$title" $1/$filename
fi
done < $1/feed.sample.xml

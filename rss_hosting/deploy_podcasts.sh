#!/bin/bash
echo $1
timestamp=$(date +%y%m%d_%H%M%S)
mv public/rss.xml public/rss_$timestamp.xml
rss_sample=$(cat $1/feed.sample.xml)
echo "
<rss version=\"2.0\" xmlns:itunes=\"http://www.itunes.com/dtds/podcast-1.0.dtd\">
    <script />
    <channel>
        <title>Noan's podcasts</title>
        <link>https://podcasts-noan.web.app/rss.xml</link>
        <description>An auto generated podcast playlist</description>
        <language>fr</language>
        <copyright>Radio France, Timeline</copyright>
        $rss_sample
    </channel>
</rss>
" > public/rss.xml

cp $1/*.mp3 public
firebase deploy
echo "Now go on https://www.playrun.app/podcast and add the private podcast with the url https://podcasts-noan.web.app/rss.xml"

const getPodcasts = () => {
    return new Promise((resolve) => {
        chrome.storage.local.get("podcast-list", (list) => {
            if (list != {}) {
                resolve(list["podcast-list"])
            } else {
                resolve([])
            }
        })
    })
}

const parseTitle = title => title.replace(/[^A-Z0-9]/ig, "_") + ".mp3"

const downloadPodcasts = async () => {
    const podcasts = await getPodcasts()
    const rssSample = podcasts.map(p => `
    <item>
        <title>${p.title}</title>
        <enclosure
            url="https://podcasts-noan.web.app/${parseTitle(p.title)}"
            type="audio/mpeg"
        />
        <itunes:duration>${p.duration}</itunes:duration>
        <pubDate>Thu, 04 Jan 2024</pubDate>
    </item>
    `).join("")
    chrome.downloads.download({ url: 'data:text/xml;charset=utf-8,' + rssSample, filename: "podcast_creator/feed.sample.xml" })
    podcasts.forEach(p => {
        const filename = "podcast_creator/" + parseTitle(p.title)
        chrome.downloads.download({ url: p.url, filename });
    })

}

document.getElementById("download-podcasts").addEventListener("click", downloadPodcasts)

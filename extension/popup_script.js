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

/**
 * Replaces everything that is not an ascii char to make the title usable as a filename
 * @param {string} title 
 * @returns {string} the file name
 */
const getFileName = title => title.replace(/[^A-Z0-9]/ig, "_") + ".mp3"

/**
 * Remove hash from title because it creates a bug in the
 * @param {string} title 
 * @returns The title without hash
 */
const noHash = title => title.replace(/#/g, "")

/**
 * Asks the user to download 
 * 1. A sample of the RSS feed containing all the podcast
 * 2. Each of the podcasts
 */
const downloadPodcasts = async () => {
    const podcasts = await getPodcasts()
    const rssSample = podcasts.map(p => `
    <item>
        <title>${noHash(p.title)}</title>
        <enclosure
            url="https://podcasts-noan.web.app/${getFileName(p.title)}"
            type="audio/mpeg"
        />
        <itunes:duration>${p.duration}</itunes:duration>
        <pubDate>Thu, 04 Jan 2024</pubDate>
    </item>
    `).join("")
    chrome.downloads.download({ url: 'data:text/xml;charset=utf-8,' + rssSample, filename: "podcast_creator/feed.sample.xml" })
    podcasts.forEach(p => {
        const filename = "podcast_creator/" + getFileName(p.title)
        chrome.downloads.download({ url: p.url, filename });
    })

}

const openPodcastWindow = () => {
    console.log("popup sends message")
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action:"toggle_podcast_window"}, function(response){
            console.log("got response", response)
        });
    });
    
}

document.getElementById("download-podcasts").addEventListener("click", downloadPodcasts)
document.getElementById("toggle-podcast-window").addEventListener("click", openPodcastWindow)

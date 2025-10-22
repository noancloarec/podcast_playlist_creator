/**
 * Representation of a podcast
 * @typedef {Object} Podcast
 * @property {string} title the podcast's title
 * @property {string} url the url of the media file containing the podcast
 */

/**
 * Retrieves the list of podcasts from the local storage
 * @returns {Promise<Array<Podcast>>} The list of podcasts in the local storage
 */
const getPodcasts = () => {
    return new Promise((resolve) => {
        browser.storage.local.get("podcast-list", (list) => {
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
 * @param {string} title the podcast's title
 * @returns {string} the file name
 */
const removeSpecialChars = title => title.replace(/[^A-Z0-9]/ig, "_")


/**
 * Remove hash from title because it creates a bug in my podcasts app
 * @param {string} title the podcast's title
 * @returns The title without hash
 */
const removeHashes = title => title.replace(/#/g, "")

/**
 * Remove the non latin characters from the title, otherwise eyeD3 cannot set the title properly
 * @param {string} title the podcast's title
 * @returns the string with non-latin characters removed
 */
const removeNonLatinCharacters = title => title.replace(/[\u0250-\ue007]/g, '');

/**
 * Generate the data url for an xml file
 */
const getDataUrlForXML = xmlData => {
    const blob = new Blob([xmlData], {type: "text/xml;charset=utf-8"})
    return URL.createObjectURL(blob)
}

/**
 * Asks the user to download 
 * 1. A sample of the RSS feed containing all the podcast
 * 2. Each of the podcasts
 * @param {string} targetDirectory the sub-directoy in the download folder where to store the podcasts
 */
const downloadPodcasts = async (targetDirectory) => {
    const podcasts = await getPodcasts()
    const rssSample = podcasts.map(p => `
    <item>
        <title>${removeNonLatinCharacters(removeHashes(p.title))}</title>
        <enclosure
            url="https://podcasts-noan.web.app/${removeSpecialChars(p.title)}.mp3"
            type="audio/mpeg"
        />
        <itunes:duration>${p.duration}</itunes:duration>
        <pubDate>Thu, 04 Jan 2024</pubDate>
    </item>
    `).join("")
    browser.downloads.download({ url: getDataUrlForXML(rssSample), filename: `${targetDirectory}/feed.sample.xml` })
    podcasts.forEach(p => {
        const urlWithoutGetParameters = p.url.split("?")[0]
        const extension = urlWithoutGetParameters.split(".").at(-1)
        const filename = `${targetDirectory}/${removeSpecialChars(p.title)}.${extension}`
        console.log("computed url and filname")
        console.log({ url: p.url, filename })
        console.log({ urlWithoutGetParameters, extension })
        browser.downloads.download({ url: p.url, filename });
    })

}

/**
 * Sends a message to the content script to toggle the podcast window
 */
const openPodcastWindow = () => {
    browser.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        browser.tabs.sendMessage(tabs[0].id, { action: "toggle_podcast_window" }, function (response) {
            console.log("got response", response)
        });
    });

}

document.getElementById("download-podcasts").addEventListener("click", () => downloadPodcasts("podcast_creator"))
document.getElementById("download-podcasts-to-be-cut").addEventListener("click", () => downloadPodcasts("podcasts_to_cut"))
document.getElementById("toggle-podcast-window").addEventListener("click", openPodcastWindow)

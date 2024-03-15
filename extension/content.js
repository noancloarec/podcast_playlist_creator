/**
 * Representation of a podcast
 * @typedef {Object} Podcast
 * @property {string} title the podcast's title
 * @property {string} url the url of the mp3 file containing the podcast
 * @property {string} duration the podcast's duration in the format mm:ss or hh:mm:ss
 */

/**
 * Retrieves the list of podcasts from the local storage
 * @returns {Promise<Array<Podcast>>} The list of podcasts in the local storage
 */
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
 * The podcast currently being selected.
 * @type {Podcast}
 */
let currentPodcast = {
    url: "",
    title: "",
    duration: "",
}

/**
 * The id of the input currently selected
 * On a click on an html element from the page, the text of the element being clicked will fill this input
 * This is used to set the duration and the title of the current podcast
 */
let selectedInput = "title-holder"

    
/**
 * Save the podcast list in parameter in chrome storage
 * @param {Array<Podcast>} podcastList 
 */
const savePodcasts = async (podcastList) => {
    await chrome.storage.local.set({ "podcast-list": podcastList })
}

/**
 * Display the podcasts in parameter in the podcasts window
 * @param {Array<Podcast>} podcastList 
 */
const displayPodcasts = (podcastList) => {
    const ul = document.getElementById("podcast-list")
    ul.replaceChildren(...
        podcastList.map(p => {
            const li = document.createElement("li")
            const button = document.createElement("button")
            button.innerText = "X"
            button.addEventListener("click", () => removePodcast(p.url))
            const span = document.createElement("span")
            span.innerText = `${p.title} - ${p.duration}`
            li.appendChild(span)
            li.appendChild(button)
            return li
        })
    )
}

/**
 * Remove a podcast from the list given its url
 * @param {string} url of the podcast to remove from the list
 */
const removePodcast = async (url) => {
    let podcasts = await getPodcasts()
    podcasts = podcasts.filter(p => p.url != url)
    await savePodcasts(podcasts)
    displayPodcasts(podcasts)
}

/**
 * Unselect all inputs for the current podcast
 */
const unselectAllInputs = () => {
    const children = document.getElementById("current-podcast-selection").children
    Array.from(children).forEach(div => div.classList.remove("selected"))
}

/**
 * Select an input to receive info about the current podcast
 * @param {string} inputId input id
 */
const selectInput = (inputId) => {
    unselectAllInputs()
    document.getElementById(inputId).parentElement.classList.add("selected")
    selectedInput = inputId
}

/**
 * Set an information about the current podcast
 * @param {Object} newProps properties to add to the podcast
 * @param {string} nextSelectedInput the id of the next input to select. If given this will change the selected
 */
const setCurrentPodcast = (newProps, nextSelectedInput) => {
    currentPodcast = { ...currentPodcast, ...newProps }
    document.getElementById("url-holder").value = currentPodcast.url
    document.getElementById("title-holder").value = currentPodcast.title
    document.getElementById("duration-holder").value = currentPodcast.duration

    if (nextSelectedInput) {
        selectInput(nextSelectedInput)
    }
}

/**
 * Display the podcast list window with the podcasts already saved in chrome storage.
 * Add the listener on the add podcast button so that the current podcast is added to the podcasts list
 */
const displayPodcastWindow = async () => {
    const dt = await (await fetch(chrome.runtime.getURL("podcast_window.html"))).text()
    const div = document.createElement("div")
    div.innerHTML = dt
    document.body.appendChild(div)
    document.getElementById("add-podcast").addEventListener("click", e => {
        e.stopPropagation()
        addCurrentPodcast()
    })
    displayPodcasts(await getPodcasts())
}

/**
 * Add the current podcast to the podcast list
 */
const addCurrentPodcast = async () => {
    let podcastList = [... (await getPodcasts()), currentPodcast]
    savePodcasts(podcastList)
    displayPodcasts(podcastList)
}

/**
 * Receives mp3 url intercepted from service worker to change the current podcast
 */
chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
    if (msg.action === "mp3_url_detected") {
        setCurrentPodcast({ url: msg.url }, "title-holder")
    }
    sendResponse(0)
});


displayPodcastWindow()

/**
 * Fill info about the current podcast whenever an element is clicked on the page
 * The content of the div clicked will be considered as either the title or the duration of the podcast
 */
document.addEventListener("click", e => {
    const divContent = e.target.innerText
    if (selectedInput == "title-holder") {
        setCurrentPodcast({ title: divContent }, "duration-holder")
    } else if (selectedInput == "duration-holder") {
        setCurrentPodcast({ duration: divContent }, "title-holder")
    }
})

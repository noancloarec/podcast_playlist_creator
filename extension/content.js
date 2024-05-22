/**
 * Representation of a podcast
 * @typedef {Object} Podcast
 * @property {string} title the podcast's title
 * @property {string} url the url of the mp3 file containing the podcast
 */

/**
 * Retrieves the list of podcasts from the local storage
 * @returns {Promise<Array<Podcast>>} The list of podcasts in the local storage
 */
const getPodcasts = () => {
    return new Promise((resolve) => {
        chrome.storage.local.get("podcast-list", (list) => {
            console.log({ list, v: list != {} })
            if (list["podcast-list"] !== undefined) {
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
}

/**
 * The id of the input currently selected
 * On a click on an html element from the page, the text of the element being clicked will fill this input
 * This is used to set the title of the current podcast
 */
let selectedInput;

let podcastWindow;


/**
 * Save the podcast list in parameter in chrome storage
 * @param {Array.<Podcast>} podcastList 
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
            li.appendChild(button)

            const span = document.createElement("span")
            span.innerText = p.title
            li.appendChild(span)
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
 * Set an information about the current podcast
 * @param {Podcast} newProps properties to add to the podcast
 */
const setCurrentPodcast = (newProps) => {
    currentPodcast = { ...currentPodcast, ...newProps }
    console.log(currentPodcast)
    document.getElementById("url-holder").value = currentPodcast.url
    document.getElementById("title-holder").value = currentPodcast.title

}

/**
 * Display the podcast list window with the podcasts already saved in chrome storage.
 * Add the listener on the add podcast button so that the current podcast is added to the podcasts list
 */
const initPodcastWindow = async () => {
    const dt = await (await fetch(chrome.runtime.getURL("podcast_window.html"))).text()
    podcastWindow = document.createElement("div")
    podcastWindow.innerHTML = dt
    document.body.appendChild(podcastWindow)
    document.getElementById("add-podcast").addEventListener("click", e => {
        e.stopPropagation()
        addCurrentPodcast()
    })
    document.getElementById("title-holder").addEventListener("focus", () => selectedInput = "title-holder")
    document.getElementById("title-holder").addEventListener("change", e => setCurrentPodcast({ title: e.target.value }))

    displayPodcasts(await getPodcasts())
    console.log(localStorage.getItem("podcastWindowIsDisplayed"))
    podcastWindow.style.display = localStorage.getItem("podcastWindowIsDisplayed") === "true"?"block":"none"
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
 * For specific sites, use their DOM structure to automatically fill in the info
 */
const tryToFindTitle = () => {
    if (location.origin.includes("radiofrance.fr")) {
        const title = document.querySelector("section.svelte-1cdrfq6>div span.svelte-1r0wuqp").textContent
        setCurrentPodcast({ title })
    } else if (location.origin.includes("timelinepodcast.fr")) {
        const title = document.querySelector("div.pdc-episode-title>div").textContent
        setCurrentPodcast({ title })
    } else if (location.origin.includes("mediapart.fr")) {
        const title = document.querySelector("h1").textContent
        setCurrentPodcast({ title })
    }
}

const togglePodcastWindow = () => {
    const shouldDisplay = localStorage.getItem("podcastWindowIsDisplayed") !== "true"
    console.log({shouldDisplay})
    podcastWindow.style.display = shouldDisplay ? "block" : "none"
    localStorage.setItem("podcastWindowIsDisplayed", (shouldDisplay).toString())
}

/**
 * Receives mp3 url intercepted from service worker to change the current podcast
 * And toggle podcast window messag
 */
chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
    if (msg.action === "mp3_url_detected") {
        setCurrentPodcast({ url: msg.url })
        setTimeout(tryToFindTitle, 800)
    } else if (msg.action === "toggle_podcast_window") {
        togglePodcastWindow()
    }
    sendResponse(0)
});



initPodcastWindow()

/**
 * If selectedInput is podcast title , the content of the div targeted by the event is set to its text
 * @param {Event} e the click event to catch
 */
const setTitleIfSelected = (e) => {
    const divContent = e.target.innerText
    console.log({ selectedInput })
    if (selectedInput == "title-holder") {
        setCurrentPodcast({ title: divContent })
    }
}

/**
 * Fill info about the current podcast whenever an element is clicked on the page
 * The content of the div clicked will be considered as  the title  of the podcast
 */
document.addEventListener("click", setTitleIfSelected)

console.log("IM the content script")

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
        chrome.storage.local.get("podcast-list", (list) => {
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
 * The last element which has been clicked, if it is a button there is a chance the title we wish to determine is close by
 * @type {HTMLElement}
 */
let lastClickedElement;




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
    ul.scroll({
        top: 10000,
        behavior: "smooth"
    })
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
    document.getElementById("url-holder").value = currentPodcast.url
    document.getElementById("title-holder").value = currentPodcast.title

}

/**
 * Display the podcast list window with the podcasts already saved in chrome storage.
 * Add the listener on the add podcast button so that the current podcast is added to the podcasts list
 */
const initPodcastWindow = async () => {
    const dt = await (await fetch(browser.runtime.getURL("podcast_window.html"))).text()
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
    podcastWindow.style.display = localStorage.getItem("podcastWindowIsDisplayed") === "true" ? "block" : "none"

    document.addEventListener("click", (event) => {       
        lastClickedElement = event.target
    })
    document.addEventListener("keydown", (event)=>{
        console.log(event)
        if(event.key==="e" && event.ctrlKey){
            addCurrentPodcast()
        }
    })
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
    console.log("Trying to find title")
    let title;
    if (location.origin.includes("radiofrance.fr")) {
        title = document.querySelector("h1.CoverEpisode-title")?.textContent.trim()
        if(!title){
            title = lastClickedElement?.closest(".CardMedia").querySelector(".CardTitle").textContent.trim()
        }
        setCurrentPodcast({ title })
    } else if (location.origin.includes("timelinepodcast.fr")) {
        title = document.querySelector("div.pdc-episode-title>div").textContent.trim()
    } else if (location.origin.includes("mediapart.fr")) {
        title = document.querySelector("h1").textContent.trim()
        setCurrentPodcast({ title })
    } else if (location.origin.includes("euradio.fr")) {
        title = document.querySelector("h1").textContent.trim()
        setCurrentPodcast({ title })
    } else if (location.origin.includes("podcasts.apple.com")) {
        title = document.querySelector("h1").textContent.trim()
        setCurrentPodcast({ title })
    }
    if(title){
        console.log(`Found title: ${title}`)
        setCurrentPodcast({ title })
    }

}

const togglePodcastWindow = () => {
    const shouldDisplay = localStorage.getItem("podcastWindowIsDisplayed") !== "true"
    podcastWindow.style.display = shouldDisplay ? "block" : "none"
    localStorage.setItem("podcastWindowIsDisplayed", (shouldDisplay).toString())
}

/**
 * Receives media url intercepted from service worker to change the current podcast
 * And toggle podcast window messag
 */
browser.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
    if (msg.action === "media_url_detected") {
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

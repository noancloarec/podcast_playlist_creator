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


let currentPodcast = {
    url: "",
    title: "",
    duration: "",
}

let selectedInput = "title-holder"


const savePodcasts = async (podcastList) => {
    console.log("saving", podcastList)
    await chrome.storage.local.set({ "podcast-list": podcastList })
}

const displayPodcasts = (podcastList) => {
    console.log(podcastList)
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
const removePodcast = async (url) => {
    let podcasts = await getPodcasts()
    podcasts = podcasts.filter(p => p.url != url)
    await savePodcasts(podcasts)
    displayPodcasts(podcasts)
}

const unselectAll = () => {
    const children = document.getElementById("current-podcast-selection").children
    Array.from(children).forEach(div => div.classList.remove("selected"))
}
const selectInput = (inputName) => {
    unselectAll()
    document.getElementById(inputName).parentElement.classList.add("selected")
    selectedInput = inputName
}
const setCurrentPodcast = (newProps, nextSelectedInput) => {
    currentPodcast = { ...currentPodcast, ...newProps }
    document.getElementById("url-holder").value = currentPodcast.url
    document.getElementById("title-holder").value = currentPodcast.title
    document.getElementById("duration-holder").value = currentPodcast.duration

    if (nextSelectedInput) {
        selectInput(nextSelectedInput)
    }
}

const displayPodcastWindow = async () => {
    const dt = await (await fetch(chrome.runtime.getURL("podcast_window.html"))).text()
    const div = document.createElement("div")
    div.innerHTML = dt
    document.body.appendChild(div)
    document.getElementById("add-podcast").addEventListener("click", e => {
        e.stopPropagation()
        addPodcast()
    })
    displayPodcasts(await getPodcasts())
}
const addPodcast = async () => {
    let podcastList = [... (await getPodcasts()), currentPodcast]
    savePodcasts(podcastList)
    displayPodcasts(podcastList)
}

chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
    if (msg.action === "mp3_url_detected") {
        setCurrentPodcast({ url: msg.url }, "title-holder")
    }
    sendResponse(0)
});


displayPodcastWindow()

document.addEventListener("click", e => {
    const divContent = e.target.innerText
    if (selectedInput == "title-holder") {
        setCurrentPodcast({ title: divContent }, "duration-holder")
    } else if (selectedInput == "duration-holder") {
        setCurrentPodcast({ duration: divContent }, "title-holder")
    }
})

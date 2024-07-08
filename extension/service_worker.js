console.log("hey im the background script")

const sendPodcastUrlToContentScript = url => {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        console.log("sending to ", tabs[0].id)
        chrome.tabs.sendMessage(tabs[0].id, { action: "media_url_detected", url: url }, function (response) {
            console.log("got response ", response)
        });
    });

}


chrome.webRequest.onHeadersReceived.addListener(
    function (details) {
        sendPodcastUrlToContentScript(details.url)
    },
    {
        urls: ["*://*/*.mp3*", "*://*/*.m4a*"]
    }
);

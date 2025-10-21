console.log("Im the background script")

const sendPodcastUrlToContentScript = url => {
    browser.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        console.log("sending to ", tabs[0].id)
        browser.tabs.sendMessage(tabs[0].id, { action: "media_url_detected", url: url }, function (response) {
            console.log("got response ", response)
        });
    });

}


browser.webRequest.onHeadersReceived.addListener(
    function (details) {
        console.log("detected mp3 or m4a", details)
        sendPodcastUrlToContentScript(details.url)
    },
    {
        urls: ["*://*/*.mp3*", "*://*/*.m4a*"]
    }
);

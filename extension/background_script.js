/**
 * Sends the url of a podcast to the content script
 * @param {string} url the link to the audio of the podcast 
 */
const sendPodcastUrlToContentScript = url => {
    browser.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        console.log("sending to ", tabs[0].id)
        browser.tabs.sendMessage(tabs[0].id, { action: "media_url_detected", url: url }, function (response) {
            console.log("got response ", response)
        });
    });

}


/**
 * Listen for mp3 or m4a requests sent by the browser, in order to record the link of the audio
 */
browser.webRequest.onHeadersReceived.addListener(
    function (details) {
        console.log("detected mp3 or m4a", details)
        sendPodcastUrlToContentScript(details.url)
    },
    {
        urls: ["*://*/*.mp3*", "*://*/*.m4a*"]
    }
);

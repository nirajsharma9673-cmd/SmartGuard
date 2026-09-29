(() => {

    function getEmailContent() {

        const messageBodies =
            document.querySelectorAll(".a3s.aiL");

        if (messageBodies.length > 0) {

            const latest =
                messageBodies[
                    messageBodies.length - 1
                ];

            return latest.innerText.trim();
        }


        const article =
            document.querySelector(
                'div[role="article"]'
            );

        if (article) {
            return article.innerText.trim();
        }


        const main =
            document.querySelector(
                'div[role="main"]'
            );

        if (main) {
            return main.innerText.trim();
        }


        return "";
    }


    chrome.runtime.onMessage.addListener(
        (message, sender, sendResponse) => {

            if (message.action === "GET_EMAIL") {

                const text =
                    getEmailContent();

                sendResponse({
                    success: Boolean(text),
                    text
                });
            }

            return true;
        }
    );

})();
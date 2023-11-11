const scrapeButtonHandler = () => {
  sendMessage("command", "scrape");
};

const sendMessage = (type, message) => {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.tabs.sendMessage(
      tabs[0].id,
      { type: type, message: message },
      function (response) {
        alert(response);
      }
    );
  });
};

const startDoc = () => {
  const scrapeButton = document.getElementById("scrape-button");
  scrapeButton.onclick = scrapeButtonHandler;
};

window.onload = startDoc;

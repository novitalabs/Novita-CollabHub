chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "ask-assistant",
    title: "Agent Sandbox",
    contexts: ["all"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  chrome.scripting.executeScript(
    {
      target: { tabId: tab.id },
      files: ["content.js"]
    },
    () => {
      chrome.tabs.sendMessage(tab.id, {
        type: "OPEN_PANEL"
      });
    }
  );
});

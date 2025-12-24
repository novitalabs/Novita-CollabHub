# **AI Code Assistant Browser Extension**

This project demonstrates how to build a browser-based code assistant using a Chrome extension and a backend server powered by Novita Sandbox.
Users can highlight code on any webpage, send it to the extension, and receive executed results plus LLM-generated explanations — all running in a secure isolated sandbox.

---

## **📁 Project Structure**

```
repo/
├── code-assistant-extension/               # Chrome extension files
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   ├── styles.css
└── main.py               # Extension server (LLM + Sandbox backend)
```

---

## **🖥️ 1. Running the Server**

Before using the extension, start the backend server that handles LLM reasoning and code execution.

### **Install Dependencies**

```bash
pip install novita-sandbox fastapi uvicorn openai
```

### **Set Your API Key**

```bash
export NOVITA_API_KEY="your_api_key_here"
```

### **Start the Server**

```bash
python main.py
```

By default, the server runs on:

```
http://localhost:8000
```

The Chrome extension will send requests to this endpoint.

---

## **🧩 2. Setting Up the Chrome Extension**

Now that the server is running, you can load the extension into Chrome.

### **Step-by-Step Setup**

#### **1. Open the Extensions Page**

* Go to `chrome://extensions/`
* Enable **Developer Mode** (top-right corner)

#### **2. Load the Extension**

* Click **Load Unpacked**
* Select the `code-assistant-extension/` folder inside this repository

Chrome will now install the extension.

#### **3. Verify Installation**

After loading:

* You should see the **Code Assistant** extension in your toolbar
* Click it to confirm the popup loads correctly

---

## **📝 3. How to Use the Extension**

1. Visit any webpage containing code
2. Highlight the code snippet
3. Right-click and choose **“Ask Code Assistant”**
4. A dialog box will appear
5. Add optional context
6. Click **Send**
7. The extension communicates with the server, executes the code in a sandbox, and returns the result plus an AI explanation

---

## **🎯 Summary**

You now have:

* A backend server that runs LLM reasoning + secure code execution
* A Chrome extension that captures highlighted code and communicates with the server
* A full workflow that turns any webpage into an interactive coding environment

Customize the UI, extend the assistant’s capabilities, or integrate more sandbox tools to build even more powerful browser-based AI experiences.
# 🛠️ Sandbox Chat Agent

A **chat-based coding assistant** that runs inside a secure sandbox.  
It connects to [Novita AI](https://novita.ai/) with function calling and allows the model to:

- Read and write files  
- Create multiple files at once  
- Run shell commands safely inside a working directory  
- Chat naturally through a **Gradio web interface**  

## ✨ Features

- 💬 **Chat UI (Gradio)** – Interact with the model in your browser.  
- 📂 **File operations** – Read and write files inside the sandbox.  
- 📑 **Batch file creation** – Create multiple files in one step.  
- ⚡ **Command execution** – Run shell commands like `ls` or `python main.py`.  
- 🔒 **Sandbox isolation** – Everything happens inside `/tmp/working-dir`.  

---

## 📦 Requirements

- Python 3.9+
- [Novita Sandbox SDK](https://pypi.org/project/novita-sandbox/)
- [Gradio](https://gradio.app/)
- [OpenAI Python SDK](https://pypi.org/project/openai/)

Install dependencies:

```bash
pip install gradio openai novita-sandbox
```

## 🔑 Setup

1. Get your **Novita AI API key** from:
   👉 [Novita Key Management](https://novita.ai/settings/key-management)

2. Export it as an environment variable:

```bash
export NOVITA_API_KEY="your_api_key_here"
```

3. Run the app:

```bash
python gradio_chat.py
```


## 🚀 Usage

When you start the app, a Gradio interface will open at:

```
http://127.0.0.1:7860
```

From the chat window you can:

* **Read a file** → `"Read /tmp/working-dir/main.py"`
* **Write a file** → `"Create a file main.py with print('Hello World')"`
* **Write multiple files** → `"Make two files: a.py and b.py with some content"`
* **Run commands** → `"ls"` or `"python main.py"`

The model decides when to call tools, and outputs (like file contents or command results) are returned in chat.

## App Demo


https://github.com/user-attachments/assets/80e45d94-99a7-4324-8524-c76c7cbbee6c


## 🛑 Cleanup

When the app closes, the sandbox is automatically terminated:

```
[DEBUG] Sandbox terminated. 👋
```

This ensures no resources are left hanging.

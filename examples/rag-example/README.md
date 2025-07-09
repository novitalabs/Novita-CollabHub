# Document and Database Analysis Chatbot

Business analytics is a critical but often complex task. While AI agents can significantly simplify this process, building and managing them can introduce new challenges. Developers often need to juggle multiple API keys and services for different Large Language Models (LLMs), embedding models, and GPU instances.

Novita AI comes with a unified solution, offering a single, streamlined API to access a wide variety of AI models and infrastructure. By doing so, it simplifies the development of powerful business analytics tools, allowing you to focus on building intelligent agents without the overhead of managing disparate services.

This is a Streamlit-based chatbot application that uses Novita AI to analyze and answer questions about your business data from two primary sources:
1.  **A collection of documents**: Supports various file formats including TXT, PDF, DOCX, XLSX, XLS, and CSV files.
2.  **A SQL Database**: Connects to a SQL database to answer questions about structured data.


## Features

- **Hybrid Analysis**: Seamlessly queries both SQL databases and a variety of document formats.
- **Natural Language to SQL**: Translates natural language questions into executable SQL queries.
- Document analysis using Novita AI
- Support for multiple file formats (TXT, PDF, DOCX, XLSX, XLS, CSV)
- Interactive chat interface
- Real-time document processing
- Detailed explanations and calculations for data analysis

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Novita AI API key:
   ```
   NOVITA_API_KEY=your_api_key_here
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run main.py
   ```
2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)
3. In the sidebar, enter the path to your documents folder
4. Click "Initialize Data Source" to load your documents
5. Start asking questions about your documents in the chat interface


#### Asking question from Database and Document

https://github.com/user-attachments/assets/2f1f1e43-ce50-4ec8-82a7-8d34203a6083


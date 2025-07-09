import streamlit as st
from query_processor import QueryProcessor
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

# Initialize session state
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Set page config
st.set_page_config(
    page_title="Document Analysis Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for button and title styling
st.markdown("""
<style>
    .stButton > button {
        background-color: #23D57C;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1fb36b;
        box-shadow: 0 4px 8px rgba(35, 213, 124, 0.3);
        transform: translateY(-2px);
    }
    .stButton > button:active {
        background-color: #1a9960;
        transform: translateY(0px);
    }
    h1 {
        color: #23D57C !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Document Analysis Chatbot using Novita")

# Check if data source is initialized
if st.session_state.processor is None:
    # Center the data source configuration
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Create centered columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🚀 Get Started")
        st.write("Initialize your data source to start chatting with your documents")
        
        # SQL Database Configuration (hidden)
        db_user = "root"
        db_password = "qwerty"
        db_host = "localhost"
        db_name = "retail_sales_db"

        # Documents Folder Configuration
        st.write("**Documents Folder Path:**")
        documents_folder = st.text_input(
            "",
            placeholder="Enter path to your documents folder (e.g., docs)",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Center the button
        button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
        with button_col2:
            if st.button("Initialize Data Source", use_container_width=True):
                try:
                    # Validate and resolve documents folder path
                    if not documents_folder:
                        st.error("Please provide a documents folder path")
                    else:
                        # Convert to absolute path
                        abs_documents_folder = os.path.abspath(documents_folder)
                        if not os.path.exists(abs_documents_folder):
                            st.error(f"Documents folder not found: {abs_documents_folder}")
                        elif not os.path.isdir(abs_documents_folder):
                            st.error(f"Path is not a directory: {abs_documents_folder}")
                        else:
                            # Initialize query processor with a dummy SQL engine
                             # Create SQL engine
                            connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
                            sql_engine = create_engine(connection_string)
                            st.session_state.processor = QueryProcessor(abs_documents_folder, sql_engine)
                            st.success("Data source initialized successfully!")
                            st.rerun()
                except Exception as e:
                    st.error(f"Error initializing data source: {str(e)}")

else:
    # Show data source status in sidebar
    with st.sidebar:
        st.header("📊 Data Source")
        st.success("✅ Data source initialized")
        if st.button("Reset Data Source"):
            st.session_state.processor = None
            st.session_state.messages = []
            st.rerun()

    # Main chat interface
    st.header("Chat Interface")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Process query
        try:
            response = st.session_state.processor.process_query(prompt)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.write(response)
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")

    # Add a clear chat button only if there are messages
    if st.session_state.messages:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

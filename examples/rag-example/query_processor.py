from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import AgentExecutor, create_sql_agent, create_react_agent
from langchain_experimental.agents.agent_toolkits import create_csv_agent,create_pandas_dataframe_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import AgentType
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.sql_database import SQLDatabase
from langchain.prompts import PromptTemplate
from langchain.tools import ReadFileTool
from langchain.schema import Document
import os
from dotenv import load_dotenv
from sqlalchemy.engine import Engine
import glob
import pandas as pd

load_dotenv()

class QueryProcessor:
    def __init__(self, documents_folder: str, sql_engine: Engine):
        self.documents_folder = documents_folder
        self.sql_engine = sql_engine
        self.llm = ChatOpenAI(
            model="google/gemma-3-27b-it",
            temperature=0,
            openai_api_key=os.getenv("NOVITA_API_KEY"),
            openai_api_base="https://api.novita.ai/v3/openai",
            default_headers={
                "X-Model-Provider": "google"
            }
        )
        self.embeddings = OpenAIEmbeddings(
            model="baai/bge-m3",
            openai_api_key=os.getenv("NOVITA_API_KEY"),
            openai_api_base="https://api.novita.ai/v3/openai",
            default_headers={
                "X-Model-Provider": "baai"
            }
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.sql_agent = None
        self._prepare_data_sources()
        
    def _prepare_data_sources(self):
        """Prepare both SQL and document data sources"""
        # Prepare SQL agent
        self._prepare_sql_agent()
        
        # Prepare document agent
        self._prepare_document_agent()
        
    def _prepare_sql_agent(self):
        """Initialize SQL agent"""
        # Convert SQLAlchemy Engine to LangChain SQLDatabase
        db = SQLDatabase(self.sql_engine)
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        self.sql_agent = create_sql_agent(
            llm=self.llm,
            toolkit=toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
         verbose=True
        )
        
    def _prepare_document_agent(self):
        """Initialize document agent using ReadFileTool and vector store"""
        # Get all supported files
        supported_files = []
        for ext in ['*.txt', '*.pdf', '*.docx', '*.xlsx', '*.xls', '*.csv']:
            supported_files.extend(glob.glob(os.path.join(self.documents_folder, ext)))
            
        print(f"\nFound {len(supported_files)} supported files in {self.documents_folder}")
        
        if supported_files:
            # Create ReadFileTool
            read_file_tool = ReadFileTool()
            
            # Create tools list
            tools = [read_file_tool]
            
            # Create the prompt template for the react agent
            prompt = PromptTemplate.from_template("""
            You are a helpful assistant that can answer questions about business documents.
            You have access to the following tools:
            
            {tools}
            
            Use the following format:
            
            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question
            
            Begin!
            
            Question: {input}
            Thought: I should read the relevant documents to find the answer
            {agent_scratchpad}
            """)
            
            agent = create_react_agent(self.llm, tools, prompt)
            self.document_agent = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=tools,
                verbose=True
            )
            print("\nDocument agent initialized successfully")
        else:
            print("\nNo documents found in the specified folder.")
            
    CSV_PROMPT_PREFIX = """
IMPORTANT: You are working with a pandas DataFrame called 'df' that has been loaded with the actual data.
DO NOT create sample data or make up data. Use ONLY the actual DataFrame 'df' that is available to you.

First, explore the DataFrame by:
1. Setting pandas display options to show all columns: pd.set_option('display.max_columns', None)
2. Check the shape of the DataFrame: print(df.shape)
3. Get the column names: print(df.columns.tolist())
4. Check the data types: print(df.dtypes)
5. Look at the first few rows: print(df.head())
6. Then answer the question using the actual data in the DataFrame.
"""
    CSV_PROMPT_SUFFIX = """
- **CRITICAL**: Use ONLY the actual data in the DataFrame. Do NOT create sample data or use fictional data.
- **ALWAYS** before giving the Final Answer, try another method to verify your results.
- Then reflect on the answers of the two methods you did and ask yourself if it answers correctly the original question.
- If you are not sure, try another method.
- FORMAT 4 FIGURES OR MORE WITH COMMAS.
- If the methods tried do not give the same result, reflect and try again until you have two methods that have the same result.
- If you still cannot arrive to a consistent result, say that you are not sure of the answer.
- If you are sure of the correct answer, create a beautiful and thorough response using Markdown.
- **DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE, ONLY USE THE RESULTS OF THE CALCULATIONS YOU HAVE DONE**.
- **ALWAYS**, as part of your "Final Answer", explain how you got to the answer on a section that starts with: "\n\nExplanation:\n".
- In the explanation, mention the column names that you used to get to the final answer.
- Show your work by displaying relevant DataFrame operations and their results.
"""

    def _process_document_query(self, query: str) -> str:
        """Process document query using CSV/Excel agents for tabular data, and LLM for unstructured data."""
        try:
            print(f"\nProcessing query: {query}")
            
            # Get all supported files
            supported_files = []
            for ext in ['*.txt', '*.pdf', '*.docx', '*.xlsx', '*.xls', '*.csv']:
                supported_files.extend(glob.glob(os.path.join(self.documents_folder, ext)))
            
            print(f"Found {len(supported_files)} supported files in {self.documents_folder}")
            
            if not supported_files:
                return "No documents found to search through."
            
            # Check for CSV/Excel files first
            csv_files = [f for f in supported_files if f.endswith('.csv')]
            excel_files = [f for f in supported_files if f.endswith(('.xlsx', '.xls'))]
            
            if csv_files:
                csv_file = csv_files[0]
                print(f"\nProcessing CSV file: {csv_file}")
                try:
                    # First try with pandas DataFrame agent
                    df = pd.read_csv(csv_file)
                    print(f"CSV loaded successfully with {len(df)} rows and columns: {df.columns.tolist()}")
                    
                    # Create the agent with improved configuration
                    print("Creating pandas DataFrame agent...")
                    agent = create_pandas_dataframe_agent(
                        self.llm,
                        df,
                        verbose=True,
                        include_df_in_prompt=False,  # Avoid token limits with large DataFrames
                        allow_dangerous_code=True,
                        max_iterations=10,
                        handle_parsing_errors=True
                    )
                    
                    # Process the query with our custom prompt
                    print(f"Processing query with agent: {query}")
                    # Improved prompt that ensures agent uses the actual DataFrame
                    prompt = f"""
You have access to a pandas DataFrame called 'df' with {len(df)} rows and the following columns: {df.columns.tolist()}.

Here are the first few rows of the data:
{df.head().to_string()}

Data types:
{df.dtypes.to_string()}

{self.CSV_PROMPT_PREFIX}

Question: {query}

{self.CSV_PROMPT_SUFFIX}
"""
                    response = agent.invoke({"input": prompt})
                    print(f"Agent response: {response}")
                    return response['output']
                    
                except Exception as e:
                    print(f"Error with pandas DataFrame agent: {str(e)}")
                    print("Trying alternative CSV agent...")
                    
                    # Fallback to CSV agent
                    try:
                        agent = create_csv_agent(
                            self.llm,
                            csv_file,
                            verbose=True,
                            allow_dangerous_code=True
                        )
                        
                        enhanced_query = f"""
{self.CSV_PROMPT_PREFIX}

Question: {query}

{self.CSV_PROMPT_SUFFIX}
"""
                        response = agent.invoke({"input": enhanced_query})
                        return response['output']
                        
                    except Exception as e2:
                        print(f"Error processing CSV file: {str(e2)}")
                        import traceback
                        print(f"Full traceback: {traceback.format_exc()}")
                        return f"Error processing CSV file: {str(e2)}"
                    
            elif excel_files:
                excel_file = excel_files[0]
                print(f"\nProcessing Excel file: {excel_file}")
                try:
                    df = pd.read_excel(excel_file)
                    print(f"Excel loaded successfully with {len(df)} rows and columns: {df.columns.tolist()}")
                    
                    # Create the agent with improved configuration
                    print("Creating pandas DataFrame agent...")
                    agent = create_pandas_dataframe_agent(
                        self.llm,
                        df,
                        verbose=True,
                        include_df_in_prompt=False,  # Avoid token limits with large DataFrames
                        allow_dangerous_code=True,
                        max_iterations=10,
                        handle_parsing_errors=True
                    )
                    
                    # Process the query with our custom prompt
                    print(f"Processing query with agent: {query}")
                    # Improved prompt that ensures agent uses the actual DataFrame
                    prompt = f"""
You have access to a pandas DataFrame called 'df' with {len(df)} rows and the following columns: {df.columns.tolist()}.

Here are the first few rows of the data:
{df.head().to_string()}

Data types:
{df.dtypes.to_string()}

{self.CSV_PROMPT_PREFIX}

Question: {query}

{self.CSV_PROMPT_SUFFIX}
"""
                    response = agent.invoke({"input": prompt})
                    print(f"Agent response: {response}")
                    return response['output']
                except Exception as e:
                    print(f"Error processing Excel file: {str(e)}")
                    import traceback
                    print(f"Full traceback: {traceback.format_exc()}")
                    return f"Error processing Excel file: {str(e)}"
            
            # For unstructured text files
            print("\nProcessing unstructured text files...")
            all_content = []
            for file_path in supported_files:
                try:
                    if file_path.endswith('.txt'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        all_content.append(Document(page_content=content, metadata={"source": file_path}))
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}")
                    continue
            
            if not all_content:
                return "Could not read any documents."
            
            # Process unstructured text using vector store
            print("Processing text with vector store...")
            chunks = self.text_splitter.split_documents(all_content)
            vector_store = FAISS.from_documents(chunks, self.embeddings)
            relevant_docs = vector_store.similarity_search(query, k=3)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            print(f"Generated context length: {len(context)}")
            response = self.llm.invoke(
                f"""Based on the following context, answer the question: {query}
                \nContext:\n{context}\n\nAnswer:"""
            )
            return response.content
            
        except Exception as e:
            print(f"Error processing document query: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return f"Error processing document query: {str(e)}"
            
    def process_query(self, query: str) -> str:
        """
        Process query using agents to intelligently decide between SQL and documents
        """
        # First try SQL agent
        try:
            print("\nTrying SQL Agent...")
            sql_result = self.sql_agent.run(query)
            no_answer_phrases = [
                "no results", "i don't know", "unknown", "not sure", "cannot answer", "don't have", "no data", "n/a"
            ]
            if sql_result and not any(phrase in sql_result.lower() for phrase in no_answer_phrases) and sql_result.strip():
                return f"From SQL Database: {sql_result}"
            else:
                print("SQL Agent could not answer, trying documents...")
        except Exception as e:
            print(f"SQL Agent Error: {str(e)}")
            print("Falling back to documents...")
            
        # If SQL agent fails or returns no results, try document processing
        try:
            print("\nProcessing documents...")
            doc_result = self._process_document_query(query)
            if doc_result:
                return f"From Documents: {doc_result}"
            else:
                print("Document processing returned no results")
        except Exception as e:
            print(f"Document Processing Error: {str(e)}")
                
        return "Could not find relevant information in either SQL database or documents." 
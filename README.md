# LLM-QA-chatbot

A Retrieval-Augmented Generation (RAG) application that allows users to "chat" with PDF documents using OpenAI's GPT model and ConversationalRetrievalChain.

## Features

- **Dual Interface**: Web app (Streamlit) and Command-line interface
- **PDF Processing**: Extracts and processes text from multiple PDF files
- **Vector Search**: Uses OpenAI embeddings with FAISS for semantic search
- **Conversational Memory**: Maintains chat history using ConversationBufferMemory
- **RAG Pipeline**: Retrieves relevant context and generates accurate answers
- **Enhanced UI**: Auto-clearing input, newest messages first, success notifications
- **Colored CLI**: ANSI color codes with emojis for better terminal experience

## Architecture Flow

![PDF Chatbot Flow](templates/pdf_chatbot_gpt.jpg)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LLM-QA-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_legacy.txt
   ```

4. **Set up OpenAI API key**
   ```bash
   # Create .env file in project root
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```
5. **Set up Cohere API key**
   ```bash
   echo "COHERE_API_KEY=your_api_key_here" > .env
   ```
## Usage

### Web Interface (Streamlit)
```bash
cd src
python app_p1.py
streamlit run app_p1.py
```

- Opens web interface at `http://localhost:8501`
- Upload PDFs using the sidebar
- Click "Process" to create embeddings
- ✅ Success notification when processing completes
- Ask questions in the chat interface (auto-clears after sending)
- Newest conversations appear at the top

```bash
cd src
python app_p3.py
streamlit run app_p3.py
```
### Command Line Interface
```bash
cd src
python app_p1.py cli
```
- 🤖 Colorful CLI with progress indicators
- Enter path to folder containing PDFs
- 📄 Real-time processing status with file names
- 🔄 Visual feedback for each processing step
- 🚀 Ready notification when setup complete
- Chat directly in terminal with colored output
- Type 'exit' to quit

```bash
cd src
python app_p1.py cli
```
Example Outputs:
- PDF Chat CLI (Cohere API)
- LLM model [default command-r-03-2025]: Select a LLM model
- Embedding model [default embed-english-v3.0]: Select an Embeding model
- Enter PDF folder path: Select a path
- Processing 1/1: Ads_cookbook.pdf
- Finished processing PDFs. Type 'exit' to quit.


## Core Process

1. **Load**: Extract text from PDF files using PyPDF2
2. **Chunk**: Split text into 500-character overlapping chunks
3. **Store**: Create OpenAI embeddings and store in FAISS vector database
4. **Retrieve & Generate**: Use ConversationalRetrievalChain to:
   - Search for relevant document chunks
   - Maintain conversation history
   - Generate contextual answers using GPT

## Requirements

- Python 3.8+
- OpenAI API key with available credits
- Cohere API key
- PDF files to process

## Dependencies

- `langchain==0.0.354` (legacy version with ConversationalRetrievalChain)
- `openai==0.28.1` (compatible with legacy LangChain)
- `streamlit` (web interface)
- `faiss-cpu` (vector database)
- `pypdf2` (PDF processing)

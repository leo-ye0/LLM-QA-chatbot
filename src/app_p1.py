import streamlit as st
import os
import glob
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain_community.llms import HuggingFacePipeline, LlamaCpp
import warnings
warnings.simplefilter("ignore")

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceEmbeddings(
    #     model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}),
        memory=memory,
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    # Display messages in reverse order (newest first), in pairs
    messages = st.session_state.chat_history
    for i in range(len(messages) - 1, 0, -2):
        # Display user message first
        st.write(user_template.replace(
            "{{MSG}}", messages[i-1].content), unsafe_allow_html=True)
        # Display bot message second
        st.write(bot_template.replace(
            "{{MSG}}", messages[i].content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with PDFs",
                       page_icon=":robot_face:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False

    st.header("Chat with PDFs :robot_face:")
    
    with st.form(key="question_form", clear_on_submit=True):
        user_question = st.text_input("Ask questions about your documents:", key="user_input")
        submit_button = st.form_submit_button("Send")
        
    if submit_button and user_question:
        if st.session_state.conversation:
            handle_userinput(user_question)
        else:
            st.warning("Please upload and process PDFs first!")

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)
                st.session_state.processing_complete = True
        
        if st.session_state.processing_complete:
            st.success("✅ Processing successful! You can now ask questions.")


def driver():
    """Command-line interface for chatting with PDFs in a folder"""
    load_dotenv()
    
    print(f"{Colors.BOLD}{Colors.CYAN}🤖 PDF Chat CLI{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}")
    
    # Get folder path from user
    pdf_folder = input(f"{Colors.YELLOW}📁 Enter the path to your PDF folder: {Colors.END}").strip()
    if not os.path.exists(pdf_folder):
        print(f"{Colors.RED}❌ Folder not found!{Colors.END}")
        return
    
    # Get all PDF files in folder
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    if not pdf_files:
        print(f"{Colors.RED}❌ No PDF files found in the folder!{Colors.END}")
        return
    
    print(f"{Colors.GREEN}✅ Found {len(pdf_files)} PDF files. Processing...{Colors.END}")
    
    # Process PDFs
    raw_text = ""
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"{Colors.CYAN}📄 Processing file {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}{Colors.END}")
        with open(pdf_file, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                raw_text += page.extract_text()
    
    # Get text chunks
    print(f"{Colors.MAGENTA}🔄 Creating text chunks...{Colors.END}")
    text_chunks = get_text_chunks(raw_text)
    
    # Create vector store
    print(f"{Colors.MAGENTA}🔄 Building vector store...{Colors.END}")
    vectorstore = get_vectorstore(text_chunks)
    
    # Create conversation chain
    print(f"{Colors.MAGENTA}🔄 Initializing conversation chain...{Colors.END}")
    conversation = get_conversation_chain(vectorstore)
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}🚀 Ready to chat! Type 'exit' to quit.{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")
    
    # Chat loop
    while True:
        user_question = input(f"{Colors.BOLD}{Colors.WHITE}You: {Colors.END}").strip()
        
        if user_question.lower() == 'exit':
            print(f"{Colors.YELLOW}👋 Goodbye!{Colors.END}")
            break
            
        if user_question:
            print(f"{Colors.CYAN}🤔 Thinking...{Colors.END}")
            response = conversation({'question': user_question})
            print(f"{Colors.GREEN}{Colors.BOLD}Bot:{Colors.END} {response['answer']}\n")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'cli':
        driver()
    else:
        main()

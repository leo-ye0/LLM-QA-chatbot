import os
import glob
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_cohere import ChatCohere, CohereEmbeddings
from htmlTemplates import css, bot_template, user_template
from dotenv import load_dotenv
import warnings


warnings.simplefilter("ignore")
load_dotenv()

class Colors:
    CYAN = '\033[96m'; GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'; BLUE = '\033[94m'
    BOLD = '\033[1m'; WHITE = '\033[97m'; MAGENTA = '\033[95m'; END = '\033[0m'


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


def get_text_chunks(text, chunk_size=500, chunk_overlap=100):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return splitter.split_text(text)


# Cohere LLM and Embeddings
def build_cohere_llm_and_embeddings(
    llm_model: str = "command-a-03-2025",               # command-a-03-2025
    emb_model: str = "embed-english-v3.0",      # embed-english-v3.0 / embed-multilingual-v3.0
    temperature: float = 0.2,
    max_tokens: int = 512,
):
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise RuntimeError("COHERE_API_KEY has not been set.")
    llm = ChatCohere(
        model=llm_model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    embeddings = CohereEmbeddings(
        model=emb_model
        # cohere_api_key=api_key 
    )
    return llm, embeddings


def get_vectorstore(text_chunks, embeddings):
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)


def get_conversation_chain(llm, vectorstore):
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4}),
        memory=memory
    )
    return chain


def handle_userinput(user_question):
    resp = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = resp['chat_history']
    msgs = st.session_state.chat_history
    for i in range(len(msgs) - 1, 0, -2):
        st.write(user_template.replace("{{MSG}}", msgs[i-1].content), unsafe_allow_html=True)
        st.write(bot_template.replace("{{MSG}}", msgs[i].content), unsafe_allow_html=True)


# Streamlit App
def main():
    load_dotenv()

    st.set_page_config(page_title="Chat with PDFs (Cohere API)", page_icon=":robot_face:")

    if not os.getenv("COHERE_API_KEY"):
        st.error("Cohere API key not found.")
        st.stop()

    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state: st.session_state.conversation = None
    if "chat_history" not in st.session_state: st.session_state.chat_history = None
    if "processing_complete" not in st.session_state: st.session_state.processing_complete = False

    st.header("Chat with PDFs (Cohere • Inference API) :robot_face:")

    with st.form(key="qform", clear_on_submit=True):
        q = st.text_input("Ask questions about your documents:", key="user_input")
        submit = st.form_submit_button("Send")

    if submit and q:
        if st.session_state.conversation:
            try:
                handle_userinput(q)
            except Exception as e:
                st.exception(e)
        else:
            st.warning("Please upload and process PDFs first!")

    with st.sidebar:
        st.subheader("Cohere Cloud Models")
        llm_model = st.text_input("LLM model", value="command-a-03-2025", help="command-r7b-12-2024 / command-r-08-2024")
        emb_model = st.text_input("Embedding model", value="embed-english-v3.0",
                                  help="embed-english-v3.0 / embed-multilingual-v3.0")
        max_new_tokens = st.slider("max_tokens", 64, 2048, 512, 64)
        temperature = st.slider("temperature", 0.0, 1.0, 0.2, 0.05)

        st.subheader("Your documents")
        pdfs = st.file_uploader("Upload your PDFs and click 'Process'", accept_multiple_files=True)

        if st.button("Process"):
            if not pdfs:
                st.warning("Please upload at least one PDF.")
            else:
                with st.spinner("Processing via Cohere APIs..."):
                    try:
                        raw = get_pdf_text(pdfs)
                        chunks = get_text_chunks(raw)

                        llm, embs = build_cohere_llm_and_embeddings(
                            llm_model=llm_model,
                            emb_model=emb_model,
                            temperature=temperature,
                            max_tokens=max_new_tokens
                        )
                        vs = get_vectorstore(chunks, embs)
                        st.session_state.conversation = get_conversation_chain(llm, vs)
                        st.session_state.processing_complete = True
                    except Exception as e:
                        st.exception(e)

        if st.session_state.processing_complete:
            st.success("Cloud processing successful! You can now ask questions.")


# CLI Driver
def driver():
    print(f"{Colors.CYAN}{Colors.BOLD} PDF Chat CLI (Cohere API){Colors.END}")

    api_key_ok = bool(os.getenv("COHERE_API_KEY"))
    if not api_key_ok:
        print(f"{Colors.RED} COHERE_API_KEY has not been set{Colors.END}")
        return

    llm_model = input(f"{Colors.YELLOW}LLM model [default command-a-03-2025]: {Colors.END}").strip() or "command-a-03-2025"
    emb_model = input(f"{Colors.YELLOW}Embedding model [default embed-english-v3.0]: {Colors.END}").strip() or "embed-english-v3.0"

    folder = input(f"{Colors.YELLOW} Enter PDF folder path: {Colors.END}").strip()
    if not os.path.exists(folder):
        print(f"{Colors.RED} Folder not found{Colors.END}"); return

    files = glob.glob(os.path.join(folder, "*.pdf"))
    if not files:
        print(f"{Colors.RED} No PDF files found{Colors.END}"); return

    raw = ""
    for i, f in enumerate(files, 1):
        print(f"{Colors.CYAN} Processing {i}/{len(files)}: {os.path.basename(f)}{Colors.END}")
        with open(f, "rb") as fp:
            r = PdfReader(fp)
            for p in r.pages:
                t = p.extract_text()
                if t: raw += t + "\n"

    chunks = get_text_chunks(raw)

    llm, embs = build_cohere_llm_and_embeddings(
        llm_model=llm_model, emb_model=emb_model, temperature=0.2, max_tokens=512
    )
    vs = FAISS.from_texts(texts=chunks, embedding=embs)
    conv = get_conversation_chain(llm, vs)

    print(f"{Colors.GREEN} Finished processing PDFs. Type 'exit' to quit.{Colors.END}")
    while True:
        q = input(f"{Colors.WHITE}{Colors.BOLD}You: {Colors.END}").strip()
        if q.lower() == "exit": break
        if q:
            try:
                ans = conv({"question": q})
                print(f"{Colors.GREEN}{Colors.BOLD}Bot:{Colors.END} {ans.get('answer', '(no answer)')}\n")
            except Exception as e:
                print(f"{Colors.RED}Error:{Colors.END} {e}\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        driver()
    else:
        main()

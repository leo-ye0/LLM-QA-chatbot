from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_cohere import ChatCohere, CohereEmbeddings
import tempfile

load_dotenv()

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
vectorstore = None
conversation_chain = None


def get_pdf_text(files: List[UploadFile]):
    text = ""
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        reader = PdfReader(tmp_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        os.remove(tmp_path)
    return text


def get_text_chunks(text):
    splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=100, length_function=len)
    return splitter.split_text(text)


def build_chain(text_chunks):
    llm = ChatCohere(
        model="command-a-03-2025",
        temperature=0.2,
        max_tokens=512
    )
    embeddings = CohereEmbeddings(model="embed-english-v3.0")
    store = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=store.as_retriever(), memory=memory)
    return chain


@app.post("/upload")
async def upload_pdfs(files: List[UploadFile]):
    global conversation_chain
    text = get_pdf_text(files)
    chunks = get_text_chunks(text)
    conversation_chain = build_chain(chunks)
    return {"status": "PDFs processed successfully"}


class Query(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(q: Query):
    global conversation_chain
    if conversation_chain is None:
        return {"error": "No PDFs processed yet."}
    res = conversation_chain({"question": q.question})
    return {"answer": res["answer"]}
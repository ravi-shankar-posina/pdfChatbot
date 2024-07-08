from fastapi import FastAPI , File , UploadFile
from fastapi.middleware.cors import CORSMiddleware

import os

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

global docs, vector_store, retriever, rag_chain
docs = None

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


template = """You are being asked to answer a question based on the following context and question. Please provide your answer in human legible format.
Give priority to the context and question provided and try to answer the question as accurately as possible. Make up an answer only when the asked question is not in the context.

{context}

Question: {question}
Answer:"""

custom_rag_prompt = PromptTemplate.from_template(template)


@app.get("/")
def read_root():
    if(docs is None):
        return {"status": 400, "message": "No docs loaded"}
    else:
        return {"status": 200, "message": "Total docs loaded: "+str(len(docs))}


@app.get("/reload_docs")
def reload_docs():
    global docs, vector_store, retriever
    loader = PyPDFDirectoryLoader("pdfs/")
    docs = loader.load_and_split()
    print("Total splits: ", len(docs))
    vectorstore = Chroma.from_documents(documents=docs, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    return {"status": 200, "message": "docs reloaded"}

@app.get("/chat")
def chat(message: str):
    global retriever, rag_chain
    if message=="":
        return {"status": 400, "message": "No message provided"}
    if docs is None:
        return {"status": 400, "message": "No docs loaded"}
    else:
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | custom_rag_prompt
            | llm
            | StrOutputParser()
        )
        ans = rag_chain.invoke(message)
        #rag_chain.clear()
        try:
            return {"status": 200, "message": ans}
        except:
            return {"status": 200, "message": ans}

@app.post("/upload_docs")
async def upload_docs(file: UploadFile = File(...)):
    global docs
    with open(os.path.join("pdfs", file.filename), "wb") as buffer:
        buffer.write(await file.read())
    reload_docs()
    return {"filename": file.filename, "status": 200, "message": "file uploaded"}

@app.get("/test")
def test():
    return {"status": 200, "message": "test successfull"}


if docs is not None:
    reload_docs()
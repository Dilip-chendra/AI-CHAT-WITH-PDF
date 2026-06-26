from fastapi import FastAPI
from pydantic import BaseModel
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openrouter import ChatOpenRouter
from secret_key import openrouter_api_key1

app = FastAPI()

model = ChatOpenRouter(
    model="openrouter/free", 
    openrouter_api_key=openrouter_api_key1
)

class PDFQueryPayload(BaseModel):
    text: str
    question: str

@app.get("/")
def hello():
    return {"Message": "Hello! Welcome To The Neural PDF Chat backend infrastructure."}

@app.post("/pdf_query")
def process_pdf_chat(payload: PDFQueryPayload):
    try:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(payload.text)
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        knowledge_base = FAISS.from_texts(chunks, embeddings)
        docs = knowledge_base.similarity_search(payload.question)
        
        chain = load_qa_chain(model, chain_type="stuff")
        response = chain.invoke({"input_documents": docs, "question": payload.question})
        
        return {"result": response["output_text"]}
    except Exception as e:
        return {"result": f"Internal document analysis runtime exception: {str(e)}"}

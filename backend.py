import os
from fastapi import FastAPI
from pydantic import BaseModel

from langchain_text_splitters import CharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openrouter import ChatOpenRouter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


try:
    from secret_key import openrouter_api_key1
except ImportError:
    openrouter_api_key1 = ""


app = FastAPI()


OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or openrouter_api_key1
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/auto")


class PDFQueryPayload(BaseModel):
    text: str
    question: str


@app.get("/")
def hello():
    return {
        "Message": "Hello! Welcome To The Lightweight Neural PDF Chat backend."
    }


@app.get("/health")
def health_check():
    return {
        "status": "running"
    }


def get_llm():
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is missing. Add it in Render Environment Variables.")

    return ChatOpenRouter(
        model=OPENROUTER_MODEL,
        openrouter_api_key=OPENROUTER_API_KEY,
        temperature=0.2
    )


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


@app.post("/pdf_query")
def process_pdf_chat(payload: PDFQueryPayload):
    try:
        if not payload.text.strip():
            return {
                "result": "No readable text found in the PDF."
            }

        if not payload.question.strip():
            return {
                "result": "Please ask a valid question."
            }

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        chunks = text_splitter.split_text(payload.text)

        if not chunks:
            return {
                "result": "Could not split the PDF text into chunks."
            }

        embeddings = get_embeddings()

        knowledge_base = InMemoryVectorStore.from_texts(
            texts=chunks,
            embedding=embeddings
        )

        docs = knowledge_base.similarity_search(
            query=payload.question,
            k=4
        )

        context = "\n\n".join([doc.page_content for doc in docs])

        llm = get_llm()

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are a helpful PDF question-answering assistant.

Answer the user's question using only the PDF context.
If the answer is not available in the context, say:
"I could not find this in the PDF."

Keep the answer clear and simple.
"""
            ),
            (
                "human",
                """
PDF Context:
{context}

Question:
{question}
"""
            )
        ])

        chain = prompt | llm | StrOutputParser()

        answer = chain.invoke({
            "context": context,
            "question": payload.question
        })

        return {
            "result": answer
        }

    except Exception as e:
        return {
            "result": f"Internal document analysis runtime exception: {str(e)}"
        }
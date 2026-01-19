import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

from langchain_text_splitters import RecursiveCharacterTextSplitter

def embed_pdf(file_path : str):
    loader = PyPDFLoader(file_path)
    document = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 100000, chunk_overlap = 10)
    #list of chunks -> chunked_documents
    chunked_documents = text_splitter.split_documents(document)

    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=int(os.getenv("CHROMA_PORT")), settings= Settings())
    embedding_funciton = SentenceTransformerEmbeddings(model_name = "all-MiniLM-L6-v2")

    Chroma.from_documents(
        documents= chunked_documents,
        embedding= embedding_funciton,
        collection_name=os.getenv("CHROMA_COLLECTION_NAME"),
        client=chroma_client
    )

def query_retrival(query: str) -> str:
    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=int(os.getenv("CHROMA_PORT")))
    collection = chroma_client.get_collection(name=os.getenv("CHROMA_COLLECTION_NAME"))

    results = collection.query(
        query_texts= query,
        n_results= 10,
        include=["documents", "distances"]
    )
    return results["documents"]
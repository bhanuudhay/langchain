import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

EMBED_MODEL = "nomic-embed-text"
INDEX_NAME = os.environ["INDEX_NAME"]


def ensure_index(dimension: int) -> None:
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    existing = {i["name"]: i for i in pc.list_indexes()}
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        return
    actual = existing[INDEX_NAME]["dimension"]
    if actual != dimension:
        raise SystemExit(
            f"Index '{INDEX_NAME}' has dimension {actual}, but {EMBED_MODEL} "
            f"produces {dimension}. Point INDEX_NAME at a {dimension}-dim index."
        )


if __name__ == "__main__":
    print("Ingesting...")
    source = Path(__file__).parent / "mediumblog1.txt"
    documents = [
        Document(
            page_content=source.read_text(encoding="utf-8"),
            metadata={"source": str(source)},
        )
    ]

    print("splitting...")
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = splitter.split_documents(documents)
    print(f"created {len(texts)} chunks")

    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    ensure_index(len(embeddings.embed_query("dimension probe")))

    print("ingesting into pinecone...")
    PineconeVectorStore.from_documents(texts, embeddings, index_name=INDEX_NAME)
    print("finished")

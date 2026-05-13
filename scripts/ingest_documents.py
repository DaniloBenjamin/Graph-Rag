import os
import glob
import hashlib
from pathlib import Path

import fitz  # PyMuPDF
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")


OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

PDF_FOLDERS = [
    "data/raw/manuals",
    "data/raw/checklists",
]

CHROMA_PATH = "vector_store/chroma"
COLLECTION_NAME = "cnc_knowledge_base"


openai_client = OpenAI(api_key=OPENAI_API_KEY)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


def extract_pdf_pages(pdf_path: str) -> list[dict]:
    """
    Extrai texto página a página de um PDF.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")

        if text and text.strip():
            pages.append(
                {
                    "source": os.path.basename(pdf_path),
                    "path": pdf_path,
                    "page": page_number,
                    "text": text.strip(),
                }
            )

    return pages


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Quebra textos longos em chunks menores.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = []

    for page in pages:
        split_texts = splitter.split_text(page["text"])

        for chunk_index, chunk_text in enumerate(split_texts):
            chunks.append(
                {
                    "source": page["source"],
                    "path": page["path"],
                    "page": page["page"],
                    "chunk_index": chunk_index,
                    "content": chunk_text,
                }
            )

    return chunks


def create_id(chunk: dict) -> str:
    """
    Cria um ID estável para cada chunk.
    """
    raw_id = f"{chunk['source']}|{chunk['page']}|{chunk['chunk_index']}|{chunk['content'][:80]}"
    return hashlib.md5(raw_id.encode("utf-8")).hexdigest()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Gera embeddings usando OpenAI.
    """
    response = openai_client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=texts,
    )

    return [item.embedding for item in response.data]


def batch_list(items: list, batch_size: int = 64):
    """
    Divide uma lista em batches.
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def ingest_documents():
    pdf_files = []

    for folder in PDF_FOLDERS:
        pdf_files.extend(glob.glob(f"{folder}/*.pdf"))

    if not pdf_files:
        print("Nenhum PDF encontrado nas pastas configuradas.")
        return

    print(f"PDFs encontrados: {len(pdf_files)}")

    all_chunks = []

    for pdf_file in pdf_files:
        print(f"Extraindo texto de: {pdf_file}")

        pages = extract_pdf_pages(pdf_file)
        chunks = chunk_pages(pages)

        print(f"  Páginas com texto: {len(pages)}")
        print(f"  Chunks criados: {len(chunks)}")

        all_chunks.extend(chunks)

    print(f"Total de chunks: {len(all_chunks)}")

    for batch in batch_list(all_chunks, batch_size=64):
        documents = [chunk["content"] for chunk in batch]
        embeddings = embed_texts(documents)
        ids = [create_id(chunk) for chunk in batch]

        metadatas = [
            {
                "source": chunk["source"],
                "path": chunk["path"],
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
            }
            for chunk in batch
        ]

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    print("Ingestão finalizada com sucesso.")
    print(f"Base vetorial salva em: {CHROMA_PATH}")
    print(f"Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    ingest_documents()
import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")


OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
CHROMA_PATH = "vector_store/chroma"
COLLECTION_NAME = "cnc_knowledge_base"


openai_client = OpenAI(api_key=OPENAI_API_KEY)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def embed_query(query: str) -> list[float]:
    response = openai_client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=query,
    )

    return response.data[0].embedding


def search_machine_manual(query: str, n_results: int = 5) -> list[dict]:
    """
    Busca trechos relevantes nos manuais da CNC.
    """

    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    output = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, metadata, distance in zip(documents, metadatas, distances):
        output.append(
            {
                "content": doc,
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "distance": distance,
            }
        )

    return output


if __name__ == "__main__":
    query = "spindle high temperature lubrication coolant"
    results = search_machine_manual(query)

    for i, item in enumerate(results, start=1):
        print("=" * 80)
        print(f"Resultado {i}")
        print(f"Fonte: {item['source']}")
        print(f"Página: {item['page']}")
        print(f"Distância: {item['distance']}")
        print(item["content"][:1000])
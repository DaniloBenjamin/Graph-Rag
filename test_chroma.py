import chromadb

client = chromadb.PersistentClient(path="./vector_store/chroma")

collection = client.get_or_create_collection(name="cnc_manuals")

collection.add(
    documents=[
        "Spindle overheating can be related to lubrication failure, coolant issues, or bearing problems."
    ],
    metadatas=[
        {"source": "test_manual", "page": 1}
    ],
    ids=["doc_001"]
)

results = collection.query(
    query_texts=["spindle high temperature"],
    n_results=1
)

print(results)
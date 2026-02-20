"""
events_agent.py
---------------
Semantic search agent for campus events.
"""

import chromadb
from sentence_transformers import SentenceTransformer
_embedder = SentenceTransformer("all-MiniLM-L6-v2")

CHROMA_DIR      = "chroma_db"
COLLECTION_NAME = "events"
DEFAULT_TOP_K   = 10


def search_events(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    Embed the query and return the top-k most semantically similar events.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    query_embedding = _embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "distances"],
    )

    events = []
    for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
        event = dict(metadata)
        event["distance"] = round(distance, 4)
        events.append(event)

    return events

"""
Milestone 4: Embedding and Retrieval Pipeline
Embeds all chunks using all-MiniLM-L6-v2 and stores them in ChromaDB.
Provides a retrieve() function for semantic search.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from ingest import build_chunks

# Load the embedding model (runs locally, no API key needed)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB client (stores data locally in ./chroma_db/)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

COLLECTION_NAME = "pitt_cs_reviews"


def embed_and_store(chunks, reset=False):
    """
    Embeds all chunks and stores them in ChromaDB with source metadata.
    If reset=True, deletes and recreates the collection first.
    """
    # Optionally reset the collection
    if reset:
        try:
            chroma_client.delete_collection(COLLECTION_NAME)
            print("Deleted existing collection.")
        except Exception:
            pass

    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    # Check if already populated
    if collection.count() > 0 and not reset:
        print(f"Collection already has {collection.count()} chunks. Skipping embedding.")
        return collection

    print(f"Embedding {len(chunks)} chunks...")

    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    # Store in ChromaDB in batches
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size].tolist()

        collection.add(
            ids=[f"{c['source']}_{c['chunk_index']}" for c in batch_chunks],
            documents=[c["text"] for c in batch_chunks],
            embeddings=batch_embeddings,
            metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in batch_chunks]
        )

    print(f"Stored {collection.count()} chunks in ChromaDB.")
    return collection


def retrieve(query, k=5):
    """
    Embeds the query and retrieves the top-k most relevant chunks.
    Returns a list of dicts with keys: text, source, distance.
    """
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": doc,
            "source": meta["source"],
            "distance": round(dist, 4)
        })

    return chunks


def test_retrieval():
    """
    Tests retrieval on 3 evaluation plan questions.
    Prints top chunks and distance scores for each.
    """
    test_queries = [
        "Does Jarrett Billingsley allow AI on assignments?",
        "Are Nick Farnan's exams open book?",
        "How difficult are Luis Oliveira's midterms?"
    ]

    for query in test_queries:
        print("\n" + "="*60)
        print(f"QUERY: {query}")
        print("="*60)
        results = retrieve(query, k=5)
        for i, chunk in enumerate(results):
            print(f"\n[{i+1}] Source: {chunk['source']} | Distance: {chunk['distance']}")
            print(f"Text: {chunk['text'][:300]}...")


if __name__ == "__main__":
    # Build chunks from documents
    chunks = build_chunks(folder_path="documents", chunk_size=500, overlap=100)

    # Embed and store (reset=True to rebuild from scratch)
    embed_and_store(chunks, reset=True)

    # Test retrieval on 3 evaluation questions
    test_retrieval()
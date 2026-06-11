"""
Milestone 3: Document Ingestion and Chunking Pipeline
Loads all .txt review files from the documents/ folder,
cleans them, and splits them into 500-char chunks with 100-char overlap.
"""

import os
import re


def load_documents(folder_path="documents"):
    """
    Loads all .txt files from the given folder.
    Returns a list of (text, filename) tuples.
    """
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append((text, filename))
            print(f"Loaded: {filename} ({len(text)} characters)")
    return documents


def clean_text(text):
    """
    Cleans raw document text by removing repeated separators,
    excess whitespace, and other formatting noise.
    """
    # Remove lines that are just dashes (section separators)
    text = re.sub(r"\n-{3,}\n", "\n", text)

    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def chunk_text(text, source, chunk_size=500, overlap=100):
    """
    Splits text into overlapping chunks of chunk_size characters.
    Returns a list of dicts with keys: text, source, chunk_index.
    """
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        # Only keep non-empty chunks
        if len(chunk) > 50:
            chunks.append({
                "text": chunk,
                "source": source,
                "chunk_index": chunk_index
            })
            chunk_index += 1

        start += chunk_size - overlap  # Move forward by (chunk_size - overlap)

    return chunks


def build_chunks(folder_path="documents", chunk_size=500, overlap=100):
    """
    Full pipeline: load → clean → chunk all documents.
    Returns a flat list of all chunk dicts across all documents.
    """
    documents = load_documents(folder_path)
    all_chunks = []

    for text, filename in documents:
        cleaned = clean_text(text)
        chunks = chunk_text(cleaned, source=filename, chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(chunks)
        print(f"  → {filename}: {len(chunks)} chunks")

    print(f"\nTotal chunks across all documents: {len(all_chunks)}")
    return all_chunks


def inspect_chunks(chunks, n=5):
    """
    Prints n random chunks for manual inspection.
    """
    import random
    sample = random.sample(chunks, min(n, len(chunks)))
    print("\n" + "="*60)
    print(f"SAMPLE CHUNKS (showing {len(sample)} of {len(chunks)} total)")
    print("="*60)
    for i, chunk in enumerate(sample):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Source: {chunk['source']} | Index: {chunk['chunk_index']}")
        print(f"Length: {len(chunk['text'])} characters")
        print(f"Text:\n{chunk['text']}")
    print("\n" + "="*60)


if __name__ == "__main__":
    # Run the full pipeline and inspect sample chunks
    chunks = build_chunks(folder_path="documents", chunk_size=500, overlap=100)
    inspect_chunks(chunks, n=5)
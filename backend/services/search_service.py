"""
Semantic Search Module (Section 4.12 of the dissertation).

Converts text into vector embeddings using a pretrained Sentence
Transformer model and stores/retrieves them from ChromaDB using cosine
similarity, so that customer questions are matched by meaning rather
than exact keywords.
"""
import uuid
import chromadb
from sentence_transformers import SentenceTransformer

from config import settings

_embedding_model = None
_chroma_client = None
_collection = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _embedding_model


def get_collection():
    """Return (creating if necessary) the ChromaDB collection used for the knowledge base."""
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        _collection = _chroma_client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate dense vector embeddings for a list of text chunks."""
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def add_document_chunks(document_id: int, file_name: str, chunks: list[str]) -> int:
    """
    Embed each chunk and store it in ChromaDB along with metadata linking
    it back to the originating document. Returns the number of chunks stored.
    """
    if not chunks:
        return 0

    collection = get_collection()
    embeddings = embed_texts(chunks)
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"document_id": document_id, "file_name": file_name, "chunk_index": i}
                 for i in range(len(chunks))]

    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return len(chunks)


def search_similar_chunks(query: str, top_k: int = None) -> list[dict]:
    """
    Embed the customer query and retrieve the most semantically similar
    document chunks from ChromaDB, ranked by cosine similarity.
    """
    top_k = top_k or settings.RAG_TOP_K
    collection = get_collection()
    query_embedding = embed_texts([query])[0]

    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    matches = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, dists):
        similarity = 1 - dist  # cosine distance -> similarity
        matches.append({"text": doc, "metadata": meta, "similarity": similarity})

    return matches


def delete_document_chunks(document_id: int):
    """Remove all chunks belonging to a document (used when a document is deleted)."""
    collection = get_collection()
    collection.delete(where={"document_id": document_id})

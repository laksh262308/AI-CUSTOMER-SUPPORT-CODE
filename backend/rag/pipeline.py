"""
Retrieval-Augmented Generation (RAG) Module (Section 4.13).

Combines semantic retrieval (search_service) with prompt construction so
that the Large Language Model generates answers grounded in verified
business documents rather than relying solely on its own internal
knowledge (see Figure 4.6: RAG Workflow).
"""
from services.search_service import search_similar_chunks
from config import settings

SYSTEM_INSTRUCTIONS = (
    "You are a helpful customer support assistant for a small business. "
    "Answer the customer's question using ONLY the information provided in "
    "the context below. If the context does not contain enough information "
    "to answer confidently, politely say that you do not have that "
    "information and suggest the customer contact support. Do not invent "
    "facts that are not present in the context."
)


def retrieve_context(query: str) -> tuple[str, list[dict]]:
    """
    Retrieve the most relevant document chunks for a query and combine
    them into a single context string for the LLM prompt.

    Returns (context_text, raw_matches). If no chunk clears the similarity
    threshold, context_text will be empty so the caller can respond
    gracefully instead of hallucinating an answer.
    """
    matches = search_similar_chunks(query)
    relevant = [m for m in matches if m["similarity"] >= settings.RAG_SIMILARITY_THRESHOLD]

    if not relevant:
        return "", matches

    context_text = "\n\n".join(
        f"[Source: {m['metadata'].get('file_name', 'unknown')}]\n{m['text']}"
        for m in relevant
    )
    return context_text, relevant


def build_prompt(query: str, context: str, conversation_history: str = "") -> str:
    """
    Construct the final prompt sent to the Large Language Model
    (Section 4.14.1 Prompt Construction).
    """
    history_block = f"\nPrevious conversation:\n{conversation_history}\n" if conversation_history else ""

    if context:
        return (
            f"{SYSTEM_INSTRUCTIONS}\n\n"
            f"Context from business documents:\n{context}\n"
            f"{history_block}\n"
            f"Customer question: {query}\n\n"
            f"Answer:"
        )

    # No relevant context found - Section 4.14.7 Handling Unknown Questions
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"No relevant business document context was found for this question.\n"
        f"{history_block}\n"
        f"Customer question: {query}\n\n"
        f"Politely explain that you do not have this information yet and "
        f"suggest contacting support."
    )

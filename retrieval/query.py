"""
Query the brain's knowledge base and return an answer as Justin.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import ANTHROPIC_API_KEY, CHROMA_PERSIST_DIR, OPENAI_API_KEY

# Edit this to match your voice, role, and personality.
SYSTEM_PROMPT = """You are Justin's digital brain — a knowledgeable assistant that answers \
questions about Justin's work, processes, projects, and responsibilities. \
Answer as if you were Justin himself, in first person, with a direct and helpful tone. \
Use only the context provided to you. If the context doesn't contain enough information \
to answer confidently, say so honestly rather than guessing. \
Keep answers clear and concise unless detail is specifically requested."""


def query(question: str) -> str:
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY,
    )
    Settings.llm = Anthropic(
        model="claude-opus-4-6",
        api_key=ANTHROPIC_API_KEY,
        system_prompt=SYSTEM_PROMPT,
    )

    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection("justin_brain")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )

    query_engine = index.as_query_engine(similarity_top_k=5)
    response = query_engine.query(question)
    return str(response)

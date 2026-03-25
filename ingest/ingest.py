"""
Ingest files or URLs into the brain's knowledge base.

Usage:
  python ingest/ingest.py --file path/to/file.pdf
  python ingest/ingest.py --url https://example.com/doc
  python ingest/ingest.py --dir path/to/folder
"""
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.web import SimpleWebPageReader
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import CHROMA_PERSIST_DIR, OPENAI_API_KEY


def _get_vector_store() -> ChromaVectorStore:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection("justin_brain")
    return ChromaVectorStore(chroma_collection=collection)


def _index_documents(documents):
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY,
    )
    vector_store = _get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(documents, storage_context=storage_context)


def ingest_file(file_path: str):
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    for doc in documents:
        doc.metadata["source"] = file_path
    _index_documents(documents)
    print(f"Ingested file: {file_path} ({len(documents)} chunk(s))")


def ingest_directory(dir_path: str):
    documents = SimpleDirectoryReader(dir_path, recursive=True).load_data()
    _index_documents(documents)
    print(f"Ingested directory: {dir_path} ({len(documents)} chunk(s))")


def ingest_url(url: str):
    documents = SimpleWebPageReader(html_to_text=True).load_data([url])
    for doc in documents:
        doc.metadata["source"] = url
    _index_documents(documents)
    print(f"Ingested URL: {url} ({len(documents)} chunk(s))")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add knowledge to Justin's brain")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to a file (PDF, DOCX, TXT, MD, etc.)")
    group.add_argument("--dir", help="Path to a folder of files")
    group.add_argument("--url", help="URL to scrape and ingest")
    args = parser.parse_args()

    if args.file:
        ingest_file(args.file)
    elif args.dir:
        ingest_directory(args.dir)
    elif args.url:
        ingest_url(args.url)

import numpy as np
import sqlite3, apsw
import json, re, os, datetime
try:
    import ollama
except:
    pass

"""
from typing import Union
from openai import OpenAI
from openai import AzureOpenAI
from mistralai import Mistral
import cohere
try:
    from google import genai
except:
    pass
"""
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL") if os.getenv("RAG_EMBEDDING_MODEL") else "paraphrase-multilingual"
#RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE")) if os.getenv("RAG_CHUNK_SIZE") else 1200
#RAG_CHUNK_OVERLAP_SIZE = int(os.getenv("RAG_CHUNK_OVERLAP_SIZE")) if os.getenv("RAG_CHUNK_OVERLAP_SIZE") else 200
RAG_QUERY_TOP_K = int(os.getenv("RAG_QUERY_TOP_K")) if os.getenv("RAG_QUERY_TOP_K") else 20


def cosine_similarity_matrix(query_vector, document_matrix):
    query_norm = np.linalg.norm(query_vector)
    document_norms = np.linalg.norm(document_matrix, axis=1, keepdims=True)
    document_norms[document_norms == 0] = 1  # Avoid division by zero
    
    similarities = np.dot(document_matrix, query_vector) / (query_norm * document_norms.flatten())
    return similarities

def get_embeddings(texts: list, model: str=RAG_EMBEDDING_MODEL, backend: str=""):
    """if backend == "openai" or model in ("text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"):
        return embed_texts_with_openai(texts=texts, model=model)
    if backend == "azure" or model in ("azure-text-embedding-3-small", "azure-text-embedding-3-large", "azure-text-embedding-ada-002"):
        return embed_texts_with_azure(texts=texts, model=model)
    elif backend == "cohere" or model in ("embed-english-v3.0", "embed-english-light-v3.0", "embed-multilingual-v3.0", "embed-multilingual-light-v3.0"):
        return embed_texts_with_cohere(texts=texts, model=model)
    elif backend == "mistral" or model in ("mistral-embed",):
        return embed_texts_with_mistral(texts=texts, model=model)
    elif backend in ("genai", "googleai", "vertexai") or model in ("text-embedding-004",):
        return embed_texts_with_genai(texts=texts, model=model)"""
    return embed_texts_with_ollama(texts=texts, model=model)

def embed_texts_with_ollama(texts: list, model: str=RAG_EMBEDDING_MODEL):
    try:
        response = ollama.embed(model=model, input=texts)
        embeddings = response.embeddings
        if not embeddings or len(embeddings) != len(texts):
            raise ValueError("Mismatch between texts and embeddings.")
        return np.array(embeddings)
    except Exception as e:
        print(f"Error embedding with Ollama: {e}")
        return None

class BibleVectorDatabase:
    """
    Sqlite Vector Database via `apsw`
    """

    def __init__(self, db_path="vectors.db", conn=None):
        self.conn = conn if conn else apsw.Connection(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def __del__(self):
        if not self.conn is None:
            self.conn.close()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                vector TEXT
            )
        """
        )

    def add(self, book, chapter, verse, text, vector):
        vector_str = json.dumps(vector.tolist())
        self.cursor.execute("INSERT INTO vectors (text, vector) VALUES (?, ?)", (f"{book} {chapter} {verse} {text}", vector_str))

    def search(self, query_vector, top_k=RAG_QUERY_TOP_K):
        self.cursor.execute("SELECT text, vector FROM vectors")
        rows = self.cursor.fetchall()
        
        if not rows:
            return []
        
        texts, vectors = zip(*[(row[0], np.array(json.loads(row[1]))) for row in rows])
        document_matrix = np.vstack(vectors)
        
        similarities = cosine_similarity_matrix(query_vector, document_matrix)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [texts[i] for i in top_indices]
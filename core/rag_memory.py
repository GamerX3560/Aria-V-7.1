"""
ARIA v7 — RAG Memory
Vector database-backed memory that never forgets.
Uses ChromaDB for local, persistent vector storage.

Every conversation is embedded and indexed. When ARIA gets a
new question, it searches ALL past conversations for relevant
context — even from months ago.
"""

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import List, Optional, Dict

log = logging.getLogger("ARIA.rag")

ARIA_DIR = Path.home() / "aria"
RAG_DIR = ARIA_DIR / "memory" / "rag"


class RAGMemory:
    """
    Retrieval-Augmented Generation memory using a local vector DB.
    
    Features:
    - Embeds all conversations into a persistent vector store
    - Semantic search across ALL past interactions
    - Temporal awareness (knows when things were discussed)
    - Automatic chunking of long messages
    - Works fully offline with local embeddings
    """

    def __init__(self, collection_name: str = "aria_memory"):
        RAG_DIR.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._fallback_store: List[dict] = []
        self._fallback_path = RAG_DIR / "fallback_memory.json"
        self._init_backend()

    def _init_backend(self):
        """Initialize ChromaDB or fall back to simple search."""
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=str(RAG_DIR / "chromadb"))
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            log.info(f"RAG Memory initialized with ChromaDB ({self._collection.count()} entries)")
        except ImportError:
            log.warning("ChromaDB not installed. Using fallback text search.")
            log.warning("Install for better memory: pip install chromadb")
            self._load_fallback()
        except Exception as e:
            log.error(f"ChromaDB init error: {e}. Using fallback.")
            self._load_fallback()

    def _load_fallback(self):
        """Load the fallback JSON-based memory."""
        try:
            with open(self._fallback_path, 'r') as f:
                self._fallback_store = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._fallback_store = []

    def _save_fallback(self):
        """Save fallback memory to disk."""
        with open(self._fallback_path, 'w') as f:
            json.dump(self._fallback_store[-10000:], f)  # Keep last 10k entries

    def store(self, text: str, metadata: dict = None):
        """
        Store a piece of text in the vector memory.
        
        Args:
            text: The text to store.
            metadata: Optional metadata (timestamp, role, topic, etc.)
        """
        if not text or len(text.strip()) < 10:
            return  # Skip very short/empty messages
        
        doc_id = hashlib.sha256(f"{text}{time.time()}".encode()).hexdigest()[:16]
        meta = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "char_count": len(text),
            **(metadata or {})
        }
        
        # Chunk long text
        chunks = self._chunk_text(text, max_chars=1000)
        
        if self._collection is not None:
            # ChromaDB backend
            try:
                ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
                metadatas = [meta for _ in chunks]
                self._collection.add(
                    documents=chunks,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                log.error(f"ChromaDB store error: {e}")
        else:
            # Fallback backend
            for chunk in chunks:
                self._fallback_store.append({
                    "id": doc_id,
                    "text": chunk,
                    "metadata": meta
                })
            self._save_fallback()

    def recall(self, query: str, n_results: int = 5) -> List[dict]:
        """
        Search memory for relevant past interactions.
        
        Args:
            query: The search query.
            n_results: Number of results to return.
            
        Returns:
            List of dicts with 'text', 'metadata', 'relevance' keys.
        """
        if not query.strip():
            return []
        
        if self._collection is not None:
            # ChromaDB semantic search
            try:
                results = self._collection.query(
                    query_texts=[query],
                    n_results=min(n_results, max(1, self._collection.count()))
                )
                
                memories = []
                if results and results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        meta = results['metadatas'][0][i] if results['metadatas'] else {}
                        dist = results['distances'][0][i] if results.get('distances') else 0
                        memories.append({
                            "text": doc,
                            "metadata": meta,
                            "relevance": round(1 - dist, 3) if dist else 1.0
                        })
                return memories
            except Exception as e:
                log.error(f"ChromaDB recall error: {e}")
                return []
        else:
            # Fallback: simple keyword matching
            return self._fallback_search(query, n_results)

    def _fallback_search(self, query: str, n_results: int) -> List[dict]:
        """Simple keyword-based search for fallback mode."""
        query_words = set(query.lower().split())
        scored = []
        
        for entry in self._fallback_store:
            text_words = set(entry["text"].lower().split())
            overlap = len(query_words & text_words)
            if overlap > 0:
                score = overlap / max(len(query_words), 1)
                scored.append({
                    "text": entry["text"],
                    "metadata": entry.get("metadata", {}),
                    "relevance": round(score, 3)
                })
        
        scored.sort(key=lambda x: x["relevance"], reverse=True)
        return scored[:n_results]

    def store_conversation(self, role: str, content: str):
        """Store a conversation message with role metadata."""
        self.store(content, metadata={"role": role, "type": "conversation"})

    def get_relevant_context(self, query: str, max_chars: int = 2000) -> str:
        """
        Get formatted relevant context from past memories.
        Ready to inject into the system prompt.
        """
        memories = self.recall(query, n_results=5)
        if not memories:
            return ""
        
        parts = ["--- 🧠 RECALLED MEMORIES (relevant past interactions) ---"]
        total_chars = 0
        
        for m in memories:
            if total_chars > max_chars:
                break
            timestamp = m["metadata"].get("timestamp", "unknown time")
            role = m["metadata"].get("role", "unknown")
            text = m["text"][:500]
            parts.append(f"[{timestamp}] ({role}): {text}")
            total_chars += len(text)
        
        parts.append("--- END MEMORIES ---")
        return "\n".join(parts)

    def get_stats(self) -> dict:
        """Get memory statistics."""
        if self._collection is not None:
            return {
                "backend": "ChromaDB",
                "total_entries": self._collection.count(),
                "storage": str(RAG_DIR / "chromadb"),
            }
        else:
            return {
                "backend": "Fallback (JSON)",
                "total_entries": len(self._fallback_store),
                "storage": str(self._fallback_path),
            }

    @staticmethod
    def _chunk_text(text: str, max_chars: int = 1000) -> List[str]:
        """Split text into chunks at sentence boundaries."""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current = ""
        sentences = text.replace("\n", ". ").split(". ")
        
        for sentence in sentences:
            if len(current) + len(sentence) > max_chars:
                if current:
                    chunks.append(current.strip())
                current = sentence
            else:
                current += ". " + sentence if current else sentence
        
        if current.strip():
            chunks.append(current.strip())
        
        return chunks if chunks else [text[:max_chars]]

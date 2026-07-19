#!/usr/bin/env python3
"""
Document Knowledge Ingestion System
=====================================
Ingests PDF documents into the consciousness engine's knowledge base.

Features:
  - PDF text extraction
  - Text chunking with overlap
  - Knowledge storage in searchable format
  - Integration with spatial allocation engine
  - Always-reachable document context
"""

import json
import time
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


@dataclass
class DocumentChunk:
    """A chunk of text from a document."""
    chunk_id: str
    doc_id: str
    page: int
    section: str
    text: str
    tokens: int
    vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentKnowledgeBase:
    """Stores and retrieves document knowledge."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.documents: Dict[str, Dict] = {}
        self.chunks: List[DocumentChunk] = []
        self.chunk_index: Dict[str, DocumentChunk] = {}
        self.word_index: Dict[str, List[str]] = {}
        self.load_knowledge()

    def load_knowledge(self):
        """Load existing knowledge from disk."""
        kb_path = self.base_path / ".knowledge_base.json"
        if kb_path.exists():
            try:
                with open(kb_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.documents = data.get("documents", {})
                # Rebuild chunks from stored data
                for chunk_data in data.get("chunks", []):
                    chunk = DocumentChunk(
                        chunk_id=chunk_data["chunk_id"],
                        doc_id=chunk_data["doc_id"],
                        page=chunk_data["page"],
                        section=chunk_data.get("section", ""),
                        text=chunk_data["text"],
                        tokens=chunk_data["tokens"],
                        vector=chunk_data.get("vector"),
                        metadata=chunk_data.get("metadata", {})
                    )
                    self.chunks.append(chunk)
                    self.chunk_index[chunk.chunk_id] = chunk
                    # Build word index
                    words = set(re.findall(r'\w+', chunk.text.lower()))
                    for word in words:
                        if word not in self.word_index:
                            self.word_index[word] = []
                        self.word_index[word].append(chunk.chunk_id)
            except Exception:
                pass

    def save_knowledge(self):
        """Save knowledge to disk."""
        kb_path = self.base_path / ".knowledge_base.json"
        data = {
            "documents": self.documents,
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "doc_id": c.doc_id,
                    "page": c.page,
                    "section": c.section,
                    "text": c.text,
                    "tokens": c.tokens,
                    "vector": c.vector,
                    "metadata": c.metadata,
                }
                for c in self.chunks
            ],
        }
        with open(kb_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def add_document(self, doc_id: str, title: str, text: str, metadata: Dict = None) -> Dict:
        """Add a document to the knowledge base."""
        self.documents[doc_id] = {
            "title": title,
            "text_length": len(text),
            "added_at": time.time(),
            "metadata": metadata or {},
        }
        return {"success": True, "doc_id": doc_id, "title": title}

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    def add_chunks(self, doc_id: str, chunks: List[str], page_offset: int = 0, section: str = ""):
        """Add chunks to the knowledge base."""
        for i, text in enumerate(chunks):
            chunk_id = hashlib.sha256(f"{doc_id}:{i}:{text[:50]}".encode()).hexdigest()[:16]
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                page=page_offset + i + 1,
                section=section,
                text=text,
                tokens=len(text.split()),
                metadata={"source": doc_id}
            )
            self.chunks.append(chunk)
            self.chunk_index[chunk_id] = chunk
            # Build word index
            words = set(re.findall(r'\w+', text.lower()))
            for word in words:
                if word not in self.word_index:
                    self.word_index[word] = []
                self.word_index[word].append(chunk_id)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search knowledge base for relevant chunks."""
        query_words = set(re.findall(r'\w+', query.lower()))
        scores: Dict[str, float] = {}
        
        for word in query_words:
            if word in self.word_index:
                for chunk_id in self.word_index[word]:
                    scores[chunk_id] = scores.get(chunk_id, 0) + 1
        
        # Sort by score
        sorted_chunks = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for chunk_id, score in sorted_chunks:
            chunk = self.chunk_index.get(chunk_id)
            if chunk:
                results.append({
                    "chunk_id": chunk_id,
                    "doc_id": chunk.doc_id,
                    "page": chunk.page,
                    "section": chunk.section,
                    "text": chunk.text[:500],
                    "score": score,
                    "tokens": chunk.tokens,
                })
        
        return results

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document metadata."""
        return self.documents.get(doc_id)

    def get_all_documents(self) -> List[Dict]:
        """Get all documents."""
        return [
            {"doc_id": k, **v}
            for k, v in self.documents.items()
        ]

    def get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "total_tokens": sum(c.tokens for c in self.chunks),
            "word_index_size": len(self.word_index),
        }


class PDFIngestor:
    """Ingests PDF documents into the knowledge base."""

    def __init__(self, knowledge_base: DocumentKnowledgeBase):
        self.knowledge_base = knowledge_base

    def ingest_pdf(self, pdf_path: str, doc_id: str = None, title: str = None, 
                   chunk_size: int = 500, overlap: int = 100) -> Dict:
        """Ingest a PDF document."""
        if not HAS_PYPDF:
            return {"success": False, "error": "pypdf not available"}

        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            return {"success": False, "error": f"PDF not found: {pdf_path}"}

        try:
            reader = pypdf.PdfReader(str(pdf_file))
            total_pages = len(reader.pages)
            
            # Extract all text
            full_text = ""
            page_texts = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    page_texts.append(text)
                    full_text += f"\n\n--- Page {i+1} ---\n\n{text}"
            
            # Generate doc_id if not provided
            if not doc_id:
                doc_id = hashlib.sha256(full_text[:1000].encode()).hexdigest()[:16]
            
            # Add document
            title = title or pdf_file.stem
            self.knowledge_base.add_document(doc_id, title, full_text, {
                "source": str(pdf_file),
                "pages": total_pages,
                "file_size": pdf_file.stat().st_size,
            })
            
            # Chunk and add
            chunks = self.knowledge_base.chunk_text(full_text, chunk_size, overlap)
            self.knowledge_base.add_chunks(doc_id, chunks, section="full_text")
            
            # Save knowledge
            self.knowledge_base.save_knowledge()
            
            return {
                "success": True,
                "doc_id": doc_id,
                "title": title,
                "pages": total_pages,
                "total_chunks": len(chunks),
                "total_tokens": sum(len(c.split()) for c in chunks),
                "text_length": len(full_text),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

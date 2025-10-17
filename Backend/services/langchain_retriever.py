"""
LangChain-based Retriever using FAISS and BM25

This module provides a hybrid retrieval system using:
- FAISS for semantic search (dense retrieval)
- BM25 for keyword search (sparse retrieval)
- Reciprocal Rank Fusion for combining results
"""

import os
import joblib
import numpy as np
from typing import List, Dict, Tuple, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from rank_bm25 import BM25Okapi
import pandas as pd
import faiss as faiss_lib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs")


def path_magic(path: str) -> bool:
    """Return True if file is gzip-compressed (even without .gz extension)."""
    try:
        with open(path, 'rb') as f:
            magic = f.read(2)
            return magic == b'\x1f\x8b'
    except:
        return False


def safe_read_tsv(path: str) -> pd.DataFrame:
    """
    Read a TSV file safely with gzip detection and encoding fallback.
    Skips bad lines.
    """
    compression = 'gzip' if path.endswith('.gz') or path_magic(path) else None
    encodings = ['utf-8', 'latin1', 'cp1252']

    for enc in encodings:
        try:
            df = pd.read_csv(
                path,
                sep='\t',
                engine='python',
                encoding=enc,
                compression=compression,
                on_bad_lines='skip'
            )
            return df
        except Exception as e:
            print(f"Failed to read {path} with encoding {enc}: {e}")
    raise Exception(f"Unable to read TSV file: {path}")


class HybridRetriever(BaseRetriever):
    """
    Custom hybrid retriever that combines FAISS and BM25 search results
    using Reciprocal Rank Fusion (RRF).
    """
    
    faiss_indices: Dict[str, any] = {}
    bm25_indices: Dict[str, BM25Okapi] = {}
    documents: Dict[str, List[Document]] = {}
    embeddings: HuggingFaceEmbeddings = None
    k: int = 5
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Retrieve documents using hybrid search."""
        all_results = []
        
        for source_key in self.documents.keys():
            # FAISS retrieval (semantic)
            faiss_results = self._faiss_search(query, source_key, self.k)
            
            # BM25 retrieval (keyword)
            bm25_results = self._bm25_search(query, source_key, self.k)
            
            # Combine using RRF
            combined = self._reciprocal_rank_fusion(
                [faiss_results, bm25_results]
            )
            
            all_results.extend(combined[:self.k])
        
        # Deduplicate and return top k
        seen = set()
        unique_results = []
        for doc in all_results:
            doc_id = doc.page_content[:100]  # Use content prefix as ID
            if doc_id not in seen:
                seen.add(doc_id)
                unique_results.append(doc)
        
        return unique_results[:self.k]
    
    def _faiss_search(
        self, query: str, source_key: str, k: int
    ) -> List[Tuple[Document, float]]:
        """Perform FAISS semantic search."""
        if source_key not in self.faiss_indices or source_key not in self.documents:
            return []
        
        try:
            query_embedding = self.embeddings.embed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            faiss_index = self.faiss_indices[source_key]
            distances, indices = faiss_index.search(query_vector, k)
            
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.documents[source_key]):
                    doc = self.documents[source_key][idx]
                    # Convert distance to similarity score
                    similarity = 1 / (1 + distance)
                    results.append((doc, similarity))
            
            return results
        except Exception as e:
            print(f"FAISS search error for {source_key}: {e}")
            return []
    
    def _bm25_search(
        self, query: str, source_key: str, k: int
    ) -> List[Tuple[Document, float]]:
        """Perform BM25 keyword search."""
        if source_key not in self.bm25_indices or source_key not in self.documents:
            return []
        
        try:
            tokenized_query = query.lower().split()
            bm25 = self.bm25_indices[source_key]
            scores = bm25.get_scores(tokenized_query)
            
            # Get top k indices
            top_indices = np.argsort(scores)[::-1][:k]
            
            results = []
            for idx in top_indices:
                if idx < len(self.documents[source_key]) and scores[idx] > 0:
                    doc = self.documents[source_key][idx]
                    results.append((doc, float(scores[idx])))
            
            return results
        except Exception as e:
            print(f"BM25 search error for {source_key}: {e}")
            return []
    
    def _reciprocal_rank_fusion(
        self, 
        result_lists: List[List[Tuple[Document, float]]], 
        k: int = 60
    ) -> List[Document]:
        """
        Combine multiple ranked lists using Reciprocal Rank Fusion.
        
        Args:
            result_lists: List of ranked result lists
            k: Constant for RRF formula (default 60)
        """
        doc_scores = {}
        
        for results in result_lists:
            for rank, (doc, _score) in enumerate(results, start=1):
                doc_id = doc.page_content[:100]  # Use content prefix as ID
                
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {"doc": doc, "score": 0}
                
                # RRF formula: 1 / (k + rank)
                doc_scores[doc_id]["score"] += 1 / (k + rank)
        
        # Sort by RRF score
        sorted_docs = sorted(
            doc_scores.values(), 
            key=lambda x: x["score"], 
            reverse=True
        )
        
        return [item["doc"] for item in sorted_docs]


def load_all_documents(docs_dir: str) -> Tuple[Dict, Dict, Dict]:
    """
    Load all documents dynamically from the docs folder.
    Returns FAISS indices, BM25 indices, and documents.
    """
    faiss_indices = {}
    bm25_indices = {}
    documents_dict = {}
    
    for fname in os.listdir(docs_dir):
        path = os.path.join(docs_dir, fname)
        
        # Load FAISS indices
        if fname.endswith(".faiss"):
            try:
                index = faiss_lib.read_index(path)
                key = fname.split('.')[0]
                faiss_indices[key] = index
                print(f"✓ Loaded FAISS index for {key} with {index.ntotal} vectors")
            except Exception as e:
                print(f"✗ Failed to load FAISS index {fname}: {e}")
        
        # Load BM25 indices
        elif fname.endswith("_bm25.pkl"):
            try:
                bm25_corpus = joblib.load(path)
                bm25 = BM25Okapi(bm25_corpus)
                key = fname.split('_')[0]
                bm25_indices[key] = bm25
                print(f"✓ Loaded BM25 index for {key}")
            except Exception as e:
                print(f"✗ Failed to load BM25 file {fname}: {e}")
        
        # Load document data
        elif fname.endswith("_data.pkl"):
            try:
                data = joblib.load(path)
                key = fname.split('_')[0]
                
                # Convert to LangChain Documents
                docs = []
                if isinstance(data, list):
                    for i, item in enumerate(data):
                        if isinstance(item, dict):
                            content = item.get('content', str(item))
                            metadata = {k: v for k, v in item.items() if k != 'content'}
                            docs.append(Document(page_content=content, metadata=metadata))
                        else:
                            docs.append(Document(page_content=str(item), metadata={"index": i}))
                
                documents_dict[key] = docs
                print(f"✓ Loaded {len(docs)} documents for {key}")
            except Exception as e:
                print(f"✗ Failed to load data file {fname}: {e}")
        
        # Load TSV files as fallback (including .tsv.gz)
        elif fname.endswith(".tsv") or fname.endswith(".tsv.gz"):
            try:
                df = safe_read_tsv(path)
                key = fname.replace('.tsv.gz', '').replace('.tsv', '')
                
                docs = []
                for idx, row in df.iterrows():
                    content = row.get('content', str(row.to_dict()))
                    metadata = row.to_dict()
                    if 'content' in metadata:
                        del metadata['content']
                    docs.append(Document(page_content=content, metadata=metadata))
                
                documents_dict[key] = docs
                print(f"✓ Loaded {len(docs)} documents from TSV for {key}")
            except Exception as e:
                print(f"✗ Failed to load TSV {fname}: {e}")
    
    return faiss_indices, bm25_indices, documents_dict


def create_hybrid_retriever(k: int = 5) -> HybridRetriever:
    """
    Create and initialize a hybrid retriever with FAISS and BM25.
    
    Args:
        k: Number of documents to retrieve
    
    Returns:
        Initialized HybridRetriever instance
    """
    print("\n🔧 Initializing Hybrid Retriever...")
    
    # Load embeddings model
    print("📦 Loading embeddings model...")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name='nlpaueb/legal-bert-base-uncased',
            model_kwargs={'device': 'cpu'}
        )
        print("✓ Loaded legal-bert-base-uncased")
    except Exception as e:
        print(f"⚠ Failed to load legal-bert, using fallback: {e}")
        embeddings = HuggingFaceEmbeddings(
            model_name='all-MiniLM-L6-v2',
            model_kwargs={'device': 'cpu'}
        )
        print("✓ Loaded all-MiniLM-L6-v2 (fallback)")
    
    # Load all indices and documents
    faiss_indices, bm25_indices, documents = load_all_documents(DOCS_DIR)
    
    # Create retriever
    retriever = HybridRetriever(
        faiss_indices=faiss_indices,
        bm25_indices=bm25_indices,
        documents=documents,
        embeddings=embeddings,
        k=k
    )
    
    print(f"✓ Hybrid Retriever initialized with {len(documents)} document sources")
    return retriever


# Legacy function for backward compatibility
def retrieve_doc(query: str, top_k: int = 5) -> Tuple[List[str], List[str]]:
    """
    Legacy retrieval function for backward compatibility.
    Returns (content_list, filename_list)
    """
    retriever = create_hybrid_retriever(k=top_k)
    docs = retriever.invoke(query)
    
    content_list = [doc.page_content for doc in docs]
    filename_list = [
        doc.metadata.get('name', doc.metadata.get('filename', f'doc_{i}'))
        for i, doc in enumerate(docs)
    ]
    
    return content_list, filename_list

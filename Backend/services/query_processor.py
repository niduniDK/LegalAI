import os
import joblib
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd
from rank_bm25 import BM25Okapi
import re
import csv

# Support both local and Railway/production paths
if os.path.exists("/app/data"):
    DATA_DIR = "/app/data"  # Railway Volume mount path
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")  # Local development

# Subfolders for different data types
INDICES_DIR = os.path.join(DATA_DIR, "indices")  # For .faiss, .pkl, .tsv files
MODELS_DIR = os.path.join(DATA_DIR, "models")     # For Legal-BERT model

# Load Sentence Transformer model
legal_bert_path = os.path.join(MODELS_DIR, "legal-bert-base-uncased")

# Temporarily allow startup without models for initial deployment
model = None
if not os.path.exists(legal_bert_path):
    print(f"⚠️ Legal-BERT not found at {legal_bert_path}. Service will start but queries will fail.")
    print(f"   Run 'python download_models.py' inside the container to download models.")
else:
    try:
        model = SentenceTransformer(legal_bert_path)
        print(f"✓ Loaded Legal-BERT from {legal_bert_path}")
    except Exception as e:
        print(f"⚠️ Failed to load Legal-BERT: {e}")

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

def path_magic(path: str) -> bool:
    """Return True if file is gzip-compressed (even without .gz extension)."""
    try:
        with open(path, 'rb') as f:
            magic = f.read(2)
            return magic == b'\x1f\x8b'
    except:
        return False

def load_all_documents(docs_dir: str):
    """
    Load all documents dynamically from the docs folder.
    Supports: .faiss, _bm25.pkl, _data.pkl, .tsv
    """
    sources = {}
    
    # Check if directory exists
    if not os.path.exists(docs_dir):
        print(f"⚠️ Indices directory not found: {docs_dir}")
        print(f"   Service will start but queries will fail until data is available.")
        return sources
    
    for fname in os.listdir(docs_dir):
        path = os.path.join(docs_dir, fname)

        if fname.endswith(".faiss"):
            try:
                index = faiss.read_index(path)
                key = fname.split('.')[0]  # e.g., bills, acts, gazettes
                sources.setdefault(key, {})["faiss"] = index
                print(f"Loaded FAISS index for {key} with {index.ntotal} vectors")
            except Exception as e:
                print(f"Failed to load FAISS index {fname}: {e}")
                # Skip this file and continue

        elif fname.endswith("_bm25.pkl"):
            try:
                bm25_corpus = joblib.load(path)
                bm25 = BM25Okapi(bm25_corpus)
                key = fname.split('_')[0]  # e.g., bills, acts, gazettes
                sources.setdefault(key, {})["bm25"] = bm25
                print(f"Loaded BM25 index for {key}")
            except (EOFError, Exception) as e:
                print(f"Failed to load BM25 file {fname}: {e}")
                # Skip this file and continue

        elif fname.endswith("_data.pkl"):
            try:
                data = joblib.load(path)
                key = fname.split('_')[0]
                sources.setdefault(key, {})["data"] = data
                print(f"Loaded data for {key}")
            except (EOFError, Exception) as e:
                print(f"Failed to load data file {fname}: {e}")
                # Skip this file and continue

        elif fname.endswith(".tsv") or fname.endswith(".tsv.gz"):
            df = safe_read_tsv(path)
            key = fname.split('.')[0]
            sources.setdefault(key, {})["df"] = df

            # Ensure 'content', 'name', 'type' columns exist
            if 'content' not in df.columns:
                df['content'] = ""
            if 'name' not in df.columns:
                df['name'] = df.index.astype(str)
            if 'type' not in df.columns:
                df['type'] = ""

            sources[key]["documents"] = df['content'].tolist()
            sources[key]["metadata"] = df[["name", "type"]].to_dict(orient='records')

    return sources

# Load all documents from data/indices folder
sources = load_all_documents(INDICES_DIR)

# Print summary of loaded sources
print(f"Loaded {len(sources)} document sources:")
for key, data in sources.items():
    components = []
    if "faiss" in data:
        components.append("FAISS")
    if "bm25" in data:
        components.append("BM25")
    if "documents" in data:
        components.append(f"{len(data['documents'])} docs")
    print(f"  {key}: {', '.join(components) if components else 'No components loaded'}")

if not sources:
    print("Warning: No document sources loaded successfully!")

# Retrieval functions generalized
def faiss_retrieve(query: str, source_key: str, k: int = 5) -> List[Tuple[str, dict, float]]:
    if source_key not in sources or "faiss" not in sources[source_key]:
        return []
    
    if "documents" not in sources[source_key] or "metadata" not in sources[source_key]:
        return []
    
    index = sources[source_key]["faiss"]
    docs = sources[source_key]["documents"]
    metadata = sources[source_key]["metadata"]

    query_embedding = model.encode([query])[0]
    distances, indices = index.search(np.array([query_embedding], dtype=np.float32), k)

    results = []
    for idx, distance in zip(indices[0], distances[0]):
        if idx < len(docs):
            score = 1 / (1 + distance)
            results.append((docs[idx], metadata[idx], score))
    return results

def bm25_retrieve(query: str, source_key: str, k: int = 5) -> List[Tuple[str, dict, float]]:
    if source_key not in sources or "bm25" not in sources[source_key]:
        return []
    
    if "documents" not in sources[source_key] or "metadata" not in sources[source_key]:
        return []
    
    bm25 = sources[source_key]["bm25"]
    docs = sources[source_key]["documents"]
    metadata = sources[source_key]["metadata"]

    tokens = re.findall(r"\w+", query.lower())
    scores = bm25.get_scores(tokens)
    top_indices = np.argsort(scores)[::-1][:k]

    results = []
    for i in top_indices:
        if i < len(docs) and scores[i] > 0:
            scores[i] = (scores[i] - np.min(scores))/(np.max(scores) - np.min(scores))  # Normalize score
            results.append((docs[i], metadata[i], float(scores[i])))
    return results

def retrieve_doc(query: str, top_k: int = 5):
    """Retrieve top K documents from all sources, sorted by similarity score."""
    results_dict = {}

    for key in sources.keys():
        bm25_results = bm25_retrieve(query, key, k=top_k) if "bm25" in sources[key] else []
        faiss_results = faiss_retrieve(query, key, k=top_k) if "faiss" in sources[key] else []

        combined_results = bm25_results + faiss_results

        for doc, meta, score in combined_results:
            name = meta["name"]
            if name not in results_dict or score > results_dict[name][2]:
                results_dict[name] = (doc, meta, score)

    sorted_results = sorted(results_dict.values(), key=lambda x: x[2], reverse=True)
    final_results = sorted_results[:top_k]

    content = [doc for doc, meta, score in final_results]
    filenames = [f"{meta['type'] if meta['type'] != 'bill' else 'bills'}/{meta['name']}" for doc, meta, score in final_results]

    print(content)

    return content, filenames

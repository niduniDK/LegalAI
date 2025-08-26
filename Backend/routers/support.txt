import joblib
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import torch
import torch
from sentence_transformers import SentenceTransformer




def process_query(query: str, top_k: int = 5):
    """    Retrieve top K documents based on the query using BM25 and FAISS.

    Args:
        query (str): The query string.
        top_k (int): Number of top documents to retrieve.  
    Returns:
        List[Tuple[str, str]]: List of tuples containing document name and content.
    """

    # model = torch.load('F:/Semester 5/DSE Project/LegalAI/utils/model.pkl', map_location=torch.device('cpu'))

    torch.serialization.add_safe_globals({'sentence_transformers.SentenceTransformer.SentenceTransformer': SentenceTransformer})
    model = torch.load(
        'F:/Semester 5/DSE Project/LegalAI/utils/model.pkl',
        map_location=torch.device('cpu'),
        weights_only=False
    )

    import faiss

    index = faiss.read_index("F:/Semester 5/DSE Project/LegalAI/utils/bills_semantic_index.faiss")

    meta_data = joblib.load("F:/Semester 5/DSE Project/LegalAI/utils/meta_data.pkl")
    documents = joblib.load("F:/Semester 5/DSE Project/LegalAI/utils/documents.pkl")

    query_vector = model.encode([query])
    top_k = 5
    distances, indices = index.search(np.array(query_vector), top_k)
    
    content = []

    for dist, idx in zip(distances[0], indices[0]):
        if idx >= len(meta_data):
            print(f"Index {idx} out of bounds for meta_data with length {len(meta_data)}")
            continue
        filename, chunk_id = meta_data[idx]
        content.append(documents[idx])
        print(f"Match from {filename} (chunk {chunk_id}):\n{documents[idx]}\nConfidence: {1 / (1 + dist)}")

    return content
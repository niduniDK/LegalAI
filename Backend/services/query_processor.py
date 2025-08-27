import os
import joblib
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import torch
import torch
from sentence_transformers import SentenceTransformer
import pandas as pd
from rank_bm25 import BM25Okapi
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # current file directory
index_path = os.path.join(BASE_DIR, "..", "docs", "bills.faiss")  # go up one folder
bm25_path = os.path.join(BASE_DIR, "..", "docs", "bills_bm25.pkl")
data_path = os.path.join(BASE_DIR, "..", "docs", "bills_data.pkl")
bills_path = os.path.join(BASE_DIR, "..", "docs", "bills.tsv")

model = SentenceTransformer('nlpaueb/legal-bert-base-uncased')
index_bills = faiss.read_index(index_path)

bm25_corpus = joblib.load(bm25_path)
bm25_bills = BM25Okapi(bm25_corpus)

data = joblib.load(data_path)
bills_data = pd.read_csv(bills_path, sep='\t', compression='gzip')

documents_bills = bills_data['content'].tolist()
metadata_bills = bills_data[["name", "type"]].to_dict(orient='records')

def faiss_retrieve(query: str, k: int = 5) -> List[Tuple[str, dict, float]]:
    # FAISS embedding retrieval
    query_embedding = model.encode([query])[0]
    distances, indices = index_bills.search(np.array([query_embedding], dtype=np.float32), k)
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        if idx < len(data):
            score = 1 / (1 + distance)  # Convert L2 distance to similarity score
            results.append((documents_bills[idx], metadata_bills[idx], score))
    return results

def bm25_retrieve(query: str, k: int = 5) -> List[Tuple[str, dict, float]]:
    # BM25 keyword retrieval
    tokens = re.findall(r"\w+", query.lower())
    scores = bm25_bills.get_scores(tokens)
    top_indices = np.argsort(scores)[::-1][:k]
    results = []
    for i in top_indices:
        if scores[i] > 0:
            results.append((documents_bills[i], metadata_bills[i], float(scores[i])))
    return results


def retrieve_doc(query: str, top_k: int = 5):
    """    Retrieve top K documents based on the query using BM25 and FAISS.

    Args:
        query (str): The query string.
        top_k (int): Number of top documents to retrieve.  
    Returns:
        List[Tuple[str, str]]: List of tuples containing document name and content.
    """

    # model = torch.load('F:/Semester 5/DSE Project/LegalAI/utils/model.pkl', map_location=torch.device('cpu'))

    torch.serialization.add_safe_globals({'sentence_transformers.SentenceTransformer.SentenceTransformer': SentenceTransformer})
    # model = torch.load(
    #     SentenceTransformer('nlpaueb/legal-bert-base-uncased'),
    #     map_location=torch.device('cpu'),
    #     weights_only=False
    # )
    # meta_data_bills = joblib.load("F:/Semester 5/DSE Project/LegalAI/utils/meta_data.pkl")
    # documents_bills = joblib.load("F:/Semester 5/DSE Project/LegalAI/utils/documents.pkl")

    content = []
    filenames = []

    bm25_results = bm25_retrieve(query)
    faiss_results = faiss_retrieve(query)

    results = bm25_results + faiss_results

    for result in results:
        doc, meta, score = result

        if meta["name"] not in filenames:
            filenames.append(meta["name"])
        
        content.append(doc)

    return content, filenames
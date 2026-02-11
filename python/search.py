import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from prepare import load_theses, normalize
import re
import unicodedata
import torch

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "thesis.index"
ID_FILE = "thesis_ids.npy"
TOP_K = 10

# df = load_theses()
# index = faiss.read_index(INDEX_FILE)
# ids = np.load(ID_FILE)
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Device Used: {device}")
# print("Downloading model..")
# model = SentenceTransformer(MODEL_NAME, device=device) # Download model

def initialise(MODEL_NAME=MODEL_NAME, INDEX_FILE=INDEX_FILE, ID_FILE=ID_FILE):
    df = load_theses()
    index = faiss.read_index(INDEX_FILE)
    ids = np.load(ID_FILE)
    model = SentenceTransformer(MODEL_NAME)
    return df, index, ids, model

def search(query, df, index, ids, model, TOP_K=TOP_K):
    print("Hello world")
    q = model.encode([query], normalize_embeddings=True)
    scores, idxs = index.search(q, TOP_K)
    results = []
    for i, idx in enumerate(idxs[0]):
        row = df.iloc[ids[idx] - 1]
        row.fillna(0, inplace=True)
        results.append((row["title"], row["author"], row["year"], scores[0][i]))
    return results

if __name__ == "__main__":
    df, index, ids, model = initialise()
    while True:
        query = input("Search: ")
        query = normalize(query)
        for r in search(query):
            print(f"{r['title']} — {r['author']} ({r['year']}) [Score: {r['score']:.2f}]")
            print(f"Subject: {r['subject']}")
            print(f"Abstract: {r['abstract'][:200]}...") # First 200 characters
            print()

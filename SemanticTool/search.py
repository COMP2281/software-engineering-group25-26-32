import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from prepare import load_theses

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "thesis.index"
ID_FILE = "thesis_ids.npy"
TOP_K = 10

df = load_theses()
index = faiss.read_index(INDEX_FILE)
ids = np.load(ID_FILE)
model = SentenceTransformer(MODEL_NAME)

def search(query):
    q = model.encode([query], normalize_embeddings=True)
    scores, idxs = index.search(q, TOP_K)
    results = []
    for i, idx in enumerate(idxs[0]):
        row = df.iloc[ids[idx] - 1]
        results.append((row["title"], row["author"], row["year"], scores[0][i]))
    return results

if __name__ == "__main__":
    while True:
        query = input("Search: ")
        for r in search(query):
            print(f"{r[0]} — {r[1]} ({r[2]})")
        print()

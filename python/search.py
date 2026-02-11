import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from prepare import load_theses, normalize

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
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
    q = model.encode([query], normalize_embeddings=True)
    scores, idxs = index.search(q, TOP_K)
    results = []
    for i, idx in enumerate(idxs[0]):
        row = df.iloc[ids[idx] - 1]
        row.fillna(0, inplace=True)
        row["score"] = scores[0][i]
        results.append((row["title"], row["year"], row["abstract"], row["department"], scores[0][i]))
    return results

if __name__ == "__main__":
    df, index, ids, model = initialise()
    while True:
        query = input("Search: ")
        query = normalize(query)
        for r in search(query, df, index, ids, model):
            print(f"{r[0]} ({r[1]}) [Score: {r[4]:.2f}]")
            print(f"Department: {r[3]}")
            print(f"Abstract: {r[2][:200]}...") # First 200 characters
            print()

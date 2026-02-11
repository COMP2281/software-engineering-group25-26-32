import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from prepare import load_theses
from datetime import datetime

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "thesis.index"
ID_FILE = "thesis_ids.npy"
TOP_K = 10

# df = load_theses()
# index = faiss.read_index(INDEX_FILE)
# ids = np.load(ID_FILE)
# model = SentenceTransformer(MODEL_NAME)

def initialise(MODEL_NAME=MODEL_NAME, INDEX_FILE=INDEX_FILE, ID_FILE=ID_FILE):
    df = load_theses()
    index = faiss.read_index(INDEX_FILE)
    ids = np.load(ID_FILE)
    model = SentenceTransformer(MODEL_NAME)
    return df, index, ids, model

def search(query, df, index, ids, model, TOP_K=TOP_K, fromYear=1700, toYear=datetime.now().year, includeUnknown=False):
    results = []
    q = model.encode([query], normalize_embeddings=True)

    # By default, search for 5x the request just in case there are many results that get filtered out
    scores, idxs = index.search(q, TOP_K*5)
    for i, idx in enumerate(idxs[0]):
        try:
            row = df.iloc[ids[idx] - 1]
            year = row["year"]

            # Checks
            if not year or str(year).strip() == "":
                if not includeUnknown:
                    continue
            else:
                # Filters here
                year = int(year)
                if year < fromYear or year > toYear:
                    continue
            
            # Add it to the list of results
            results.append((row["title"], row["author"], row["year"], scores[0][i]))
            
            if len(results) >= TOP_K:
                break
        except Exception as e:
            print(f"Search error: {e}")
            break

    return results

if __name__ == "__main__":
    df, index, ids, model = initialise()
    while True:
        query = input("Search: ")
        for r in search(query, df, index, ids, model):
            print(f"{r[0]} — {r[1]} ({r[2]})")
        print()

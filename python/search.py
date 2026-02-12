import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from prepare import load_theses, normalize
import datetime

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
"""
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
"""
def search(query, df, index, ids, model, TOP_K=TOP_K, fromYear=1700, toYear=datetime.datetime.now().year, includeUnknown=False):
    q = model.encode([query], normalize_embeddings=True)
    scores, idxs = index.search(q, TOP_K*5)
    results = []
    for i, idx in enumerate(idxs[0]):
        row = df.iloc[ids[idx] - 1]
        row.fillna(0, inplace=True)
        row["score"] = scores[0][i]
        # if this gives an error "author not found" then redownload the db from https://a.piggypiggyyoinkyoink.website/dingus/db/db.db
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
            results.append((row["title"], row["author"], row["year"], row["abstract"], row["department"], scores[0][i]))
            
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
        query = normalize(query)
        for r in search(query, df, index, ids, model):
            print(f"{r[0]} - {r[1]} ({r[2]}) [Score: {r[5]:.2f}]")
            print(f"Department: {r[4]}")
            print(f"Abstract: {r[3][:200]}...") # First 200 characters
            print()

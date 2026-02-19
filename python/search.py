import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from prepare import load_theses
import datetime
from prepare import normalize
import pandas
from rapidfuzz import fuzz
from prepare import load_theses, normalize
import datetime

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
TOP_K = 10


def initialise(MODEL_NAME=MODEL_NAME, INDEX_FILE=INDEX_FILE, ID_FILE=ID_FILE):
    df = load_theses()
    index = faiss.read_index(INDEX_FILE)
    ids = np.load(ID_FILE)
    model = SentenceTransformer(MODEL_NAME)
    return df, index, ids, model

def get_all_departments(df):
    depts = df["department"].unique().tolist()
    depts.sort()
    return depts
def similarityAuthor(a, b, threshold=80):
    if not a or not b:
        return False
    return fuzz.token_sort_ratio(a, b) >= threshold

def search(query, df:pandas.DataFrame, index, ids, model, TOP_K=TOP_K, fromYear=1700, toYear=datetime.datetime.now().year, includeUnknown=False, authorField=None, deptCheckboxes=[]):
    results = []
    q = model.encode([query], normalize_embeddings=True)

    # By default, search for 5x the request just in case there are many results that get filtered out
    scores, idxs = index.search(q, TOP_K*5)
    for i, idx in enumerate(idxs[0]):
        try:
            row = df.iloc[ids[idx] - 1]
            row.fillna("0", inplace=True)
            year = row["year"]

            # Checks
            if not year or str(year).strip() == "0":
                if not includeUnknown: # Skip if year is unknown and we don't want to include unknowns
                    continue
            else:
                year = int(year)
                if year < fromYear or year > toYear: # If year is outside the range, skip
                    continue
            
            # Author filter
            author = str(row["author"]).strip().lower()
            # Fuzzy search (how similar are they to one another, if author field is filled in, it must be similar enough)
            if authorField:
                if not similarityAuthor(authorField, author):
                    # If it's filled out but can't find anything similar enough, skip
                    continue

            
            # Check if any subject checkboxes exist
            if len(deptCheckboxes) > 0 and not (len(deptCheckboxes) == 1 and deptCheckboxes[0] == ""):
                # normalize department filter
                normaCheckboxes = [d.strip().lower() for d in deptCheckboxes]
                thesis_dept = str(row["department"]).strip().lower()
                if thesis_dept not in normaCheckboxes:
                    continue


            # Add it to the list of results
            results.append((row["title"], row["author"], row["year"], row["abstract"], row["department"], row["pdf_url"], scores[0][i]))
            
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
            print(f"{r[0]} - {r[1]} ({r[2]}) [Score: {r[-1]:.2f}]")
            print(f"Department: {r[4]}")
            print(f"Abstract: {r[3][:200]}...") # First 200 characters
            print()

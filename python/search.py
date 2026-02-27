import faiss, pandas, datetime, re
import numpy as np
from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz
from prepare import load_theses, normalise

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
TOP_K = 10


def initialise(MODEL_NAME=MODEL_NAME, INDEX_FILE=INDEX_FILE, ID_FILE=ID_FILE, DB_PATH="./db/db.db"):
    df = load_theses(DB_PATH)
    index = faiss.read_index(INDEX_FILE)
    ids = np.load(ID_FILE)
    model = SentenceTransformer(MODEL_NAME)
    return df, index, ids, model

def get_all_departments(df):
    depts = df["department"].unique().tolist()
    depts.sort()
    return depts

def canonical_author(name):
    if not name:
        return None
    name = name.lower().strip()
    # Comma format
    if "," in name:
        parts = [p.strip() for p in name.split(",", 1)]  # Split only first two commas (assuming Surname, Given Name(s) format and ignores all other things like Smith, John Connor, PHD)
        if len(parts) == 2:
            last = parts[0]
            rest = parts[1]
            name = f"{rest} {last}"

    name = re.sub(r"[^\w\s]", "", name)
    tokens = name.split()

    if not tokens:
        return None

    return {
        "tokens": tokens,
        "first": tokens[0],
        "last": tokens[-1],
        "initials": [t[0] for t in tokens if t]
    }


def similarityAuthor(queryName, targetCanon):
    if not queryName or not targetCanon:
        return False
    
    t = canonical_author(targetCanon)
    q = canonical_author(queryName)
    
    # Search one name case
    if " " not in queryName:
        # Fuzzy search over each token in the target name, if any are similar enough, consider it a match
        for token in t["tokens"]:
            if fuzz.ratio(queryName, token) >= 85:
                return True

    if not q or not t:
        return False

    if fuzz.ratio(q["last"], t["last"]) < 85: # Similarity parameter might need tuning for sensitivity of spelling mistakes vs. substrings/wrong authors
        return False

    # Check if names match
    if q["first"] == t["first"]:
        return True
    
    # Check if first letters match
    if q["first"][0] == t["first"][0]:
        return True

    # Optional fuzzy fallback
    return fuzz.token_sort_ratio(queryName, " ".join(t["tokens"])) >= 85


def search(query, df:pandas.DataFrame, index, ids, model, TOP_K=TOP_K, fromYear=1700, toYear=datetime.datetime.now().year, includeUnknown=False, authorField=None, deptCheckboxes=None, recurse=False):
    results = []
    if deptCheckboxes is None:
        deptCheckboxes = []
    
    df = df.fillna("0") 
    if query.strip() == "":
        # Handle edge case where search query is blank, but author query isnt
        # Department filter
        if len(deptCheckboxes) > 0 and not (len(deptCheckboxes) == 1 and deptCheckboxes[0] == ""):
            # normalize department filter
            normaCheckboxes = [d.strip().lower() for d in deptCheckboxes]
            df = df[df["department"].apply(lambda dept: str(dept).strip().lower() in normaCheckboxes if len(normaCheckboxes) > 0 else True)]
        # Year filter
        df = df[df["year"].apply(lambda year: ((not year or str(year).strip() == "0" or int(year) >= fromYear and int(year) <= toYear) if includeUnknown else ((year and str(year).strip() != "0") and int(year) >= fromYear and int(year) <= toYear)))]
        # Author filter
        if authorField:
            df = df[df["author"].apply(lambda a: similarityAuthor(authorField, str(a.strip().lower())) if str(a).strip().lower() != "0" else False)]
            for i, row in df.iterrows():
                results.append((row["title"], row["author"], row["year"], row["abstract"], row["department"], row["pdf_url"], row["db_id"], 0.0))
                # Return correct number of results
                if len(results) >= TOP_K:
                    break
        else:
            # This should never run but its here anyways
            results = []
        return results
        
                
    q = model.encode([query], normalize_embeddings=True)

    # TODO: Recursive search with increased K perhaps?

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
            results.append((row["title"], row["author"], row["year"], row["abstract"], row["department"], row["pdf_url"], row["db_id"], float(scores[0][i])))
            
            if len(results) >= TOP_K:
                break
        except Exception as e:
            print(f"Search error: {e}")
            break


    if len(results) == 0:
        # No results were found, try recursive call once
        if recurse:
            return results
        results = search(query, df, index, ids, model, TOP_K*2, fromYear, toYear, includeUnknown, authorField, deptCheckboxes, recurse=True)
    return results

if __name__ == "__main__":
    df, index, ids, model = initialise()
    while True:
        query = input("Search: ")
        authQuery = input("Author filter (optional): ")
        query = normalise(query)
        for r in search(query, df, index, ids, model, 10, 1700, datetime.datetime.now().year, True, authQuery, None):
            print(f"{r[0]} - {r[1]} ({r[2]}) [Score: {r[-1]:.2f}]")
            print(f"PDF URL: {r[5]}")
            print(f"Department: {r[4]}")
            print(f"Abstract: {r[3][:200]}...") # First 200 characters
            print()

import os, unicodedata, re, sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
try:
    DB_PATH = os.environ.get("DB_PATH")
except:
    DB_PATH = "./db/db.db"

def normalize(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"([!?.,;:]){2,}", r"\1", text)
    return text

def load_theses():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT title, author, date, abstract, department, pdf_url, id AS db_id FROM Thesis", conn)
    conn.close()
    df = df[["title", "author", "date", "abstract", "department", "pdf_url", "db_id"]] 

    # Normalisation
    df["title"] = df["title"].apply(normalize)
    df["author"] = df["author"].apply(normalize)
    df["abstract"] = df["abstract"].fillna("").apply(normalize)
    df["department"] = df["department"].fillna("").apply(normalize)
    df["pdf_url"] = df["pdf_url"].fillna("")
    df["year"] = df["date"].astype(str).str.extract(r"((19|20)\d{2})")[0]
    df["db_id"] = df["db_id"].astype(int)

    df = df[df["title"].str.split().str.len() >= 3]
    df = df.drop_duplicates(subset="title")

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    return df[["id", "title", "author",  "abstract", "department", "year", "pdf_url", "db_id"]]

def build_text(row):
    parts = [row["title"]]
    if row.get("abstract"):
        parts.append(row["abstract"])
    if row.get("department"):
        parts.append("Department: " + row["department"])
    return ". ".join(parts)


if __name__ == "__main__":
    df = load_theses()
    print(f"Loaded {len(df)} unique thesis titles")

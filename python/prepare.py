import pandas as pd
import unicodedata
import re

INPUT_CSV = "theses_utf8.csv"

def normalize(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"([!?.,;:]){2,}", r"\1", text)
    return text

def load_theses():
    df = pd.read_csv(INPUT_CSV, encoding="utf-8", on_bad_lines="skip")
    df = df[["Title", "Author", "Date", "Abstract", "Subject Discipline"]] 

    # Normalization
    df["title"] = df["Title"].apply(normalize)
    df["author"] = df["Author"].fillna("").apply(normalize)
    df["abstract"] = df["Abstract"].fillna("").apply(normalize)
    df["subject"] = df["Subject Discipline"].fillna("").apply(normalize)
    df["year"] = df["Date"].astype(str).str.extract(r"((19|20)\d{2})")[0]

    df = df[df["title"].str.split().str.len() >= 3]
    df = df.drop_duplicates(subset="title")

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    return df[["id", "title", "author", "abstract", "subject", "year"]]

def build_text(row):
    parts = [row["title"]]
    if row["author"]:
        parts.append("Author: " + row["author"])
    if row.get("abstract"):
        parts.append(row["abstract"])
    if row.get("subject"):
        parts.append("Subject: " + row["subject"])
    return ". ".join(parts)


if __name__ == "__main__":
    df = load_theses()
    print(f"Loaded {len(df)} unique thesis titles")

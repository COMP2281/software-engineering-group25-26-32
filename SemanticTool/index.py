import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from prepare import load_theses

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "thesis.index"
ID_FILE = "thesis_ids.npy"
BATCH_SIZE = 64

df = load_theses()
titles = df["title"].tolist()
ids = df["id"].to_numpy()

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer(MODEL_NAME, device=device)

embeddings = model.encode(
    titles,
    batch_size=BATCH_SIZE,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True
)

dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

faiss.write_index(index, INDEX_FILE)
np.save(ID_FILE, ids)

print(f"Indexed {index.ntotal} titles")

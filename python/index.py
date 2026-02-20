import faiss, torch
import numpy as np
from sentence_transformers import SentenceTransformer
from prepare import load_theses, build_text

print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
BATCH_SIZE = 256

df = load_theses()
texts = [build_text(row) for _, row in df.iterrows()]
ids = df["id"].to_numpy()

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device Used: {device}")
print("Downloading model..")
model = SentenceTransformer(MODEL_NAME, device=device) # Download model

print("Embedding..")
embeddings = model.encode(
    texts,
    batch_size=BATCH_SIZE,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True
)

print("Indexing..")
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

faiss.write_index(index, INDEX_FILE)
np.save(ID_FILE, ids)

print(f"Indexed {index.ntotal} titles")

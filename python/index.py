import faiss, torch, os
import numpy as np
from sentence_transformers import SentenceTransformer
from prepare import load_theses, build_text

INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
try:
    print("PyTorch Version:", torch.__version__)
    if not torch.cuda.is_available():
        print("WARNING: CUDA not available, using CPU. Building model index will be very slow, all other features unaffected.")
    print("CUDA Device Name:", torch.cuda.get_device_name(0))
except:
    pass

def build_index(DB_PATH="./db/db.db", INDEX_FILE="durham_thesis.index", ID_FILE="durham_thesis_ids.npy"):
    MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
    BATCH_SIZE = 256

    df = load_theses(DB_PATH)
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

    print(f"Indexing to files {INDEX_FILE} and {ID_FILE}..")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, INDEX_FILE)
    np.save(ID_FILE, ids)

    print(f"Indexed {index.ntotal} titles")

if __name__ == "__main__":
    build_index()
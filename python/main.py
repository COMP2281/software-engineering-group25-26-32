from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from search import initialise, search
from pydantic import BaseModel

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
TOP_K = 10

df, index, ids, model = None, None, None, None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, index, ids, model
    #startup code here
    print("Starting up...")
    df, index, ids, model = initialise(MODEL_NAME, INDEX_FILE, ID_FILE)
    print("Startup complete.")
    yield
    #shutdown code here
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

#allow fastAPI endpoints to be accessed from localhost:8080 (the nodejs)
origins = [
    "http://localhost:*",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic model for search term
class SearchTerm(BaseModel):
    term: str
    count: int
    fromYear: int
    toYear: int
    includeUnknown: bool

@app.post("/search")
async def search_users(search_term: SearchTerm):
    results = search(search_term.term, df, index, ids, model, search_term.count, search_term.fromYear, search_term.toYear, search_term.includeUnknown)
    if not results:
        return []
    return [{"name": r[0],
             "author": r[1],
             "year": str(r[2]),
             "abstract": r[3],
             "department": r[4],
             "pdf_url": r[5]
             } for r in results]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from search import initialise, search
from pydantic import BaseModel

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "thesis.index"
ID_FILE = "thesis_ids.npy"
TOP_K = 10

df, index, ids, model = None, None, None, None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, index, ids, model
    #startup code here
    print("Starting up...")
    df, index, ids, model = initialise(MODEL_NAME, INDEX_FILE, ID_FILE)
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
    results = search(search_term.term, df, index, ids, model, 10000)
    results2 = []
    for result in results:
        year = result[2]
        if year ==0 and search_term.includeUnknown:
            results2.append(result)
        elif search_term.fromYear <= int(year) <= search_term.toYear:
            results2.append(result)
    if len(results2) > search_term.count:
        results2 = results2[:search_term.count]
    if not results2:
        return []
    return [{"name": r[0],
             "author": r[1],
             "year": str(r[2])} for r in results2]
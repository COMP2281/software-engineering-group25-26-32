from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from search import initialise, search, get_all_departments
from pydantic import BaseModel
from durham_etheses_scraper import scrape, get_last_id, get_latest_id
from get_pdf_text import upload_pdf_texts_to_db_parallel
from gemini_ai_summariser import summarise_thesis

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
TOP_K = 10

df, index, ids, model = None, None, None, None
departments = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, index, ids, model, departments
    #startup code here
    print("Starting up...")
    df, index, ids, model = initialise(MODEL_NAME, INDEX_FILE, ID_FILE)
    departments = get_all_departments(df)
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
    authorField: str
    departments: list

@app.post("/search")
async def search_users(search_term: SearchTerm):
    results = search(search_term.term, df, index, ids, model, search_term.count, search_term.fromYear, search_term.toYear, search_term.includeUnknown, authorField=search_term.authorField, deptCheckboxes=search_term.departments)
    if not results:
        return []
    return [{"name": r[0],
             "author": r[1],
             "year": str(r[2]),
             "abstract": r[3],
             "department": r[4],
             "pdf_url": r[5],
             "db_id": str(r[6])
             } for r in results]

@app.get("/departments")
async def get_departments():
    return departments

@app.post("/update-db")
# TODO: Make this permission based
# TODO: Make this not hang the server / multithreading?
# Updates the DB with new theses uploaded to Durham-Etheses, including PDF text extraction if full PDF is released.
async def update_db():
    last_id = get_last_id()
    latest_id = get_latest_id()
    print(f"Last ID in DB: {last_id}, Latest ID on site: {latest_id}")
    if last_id == latest_id:
        return {"message": "Database is already up to date"}
    for i in range(last_id + 1, latest_id + 1):
        result = scrape(i)
        if result == 0:
            print("Successfully added thesis with ID", i, "to the database.")
    upload_pdf_texts_to_db_parallel()
    return {"message": "Database updated successfully"}

@app.get("/summarise/{db_id}")
async def summarise(db_id: int):
    if True:
        summary = summarise_thesis(db_id)
    else:
        sample_file = open("./sample_summary.txt", "r")
        summary = sample_file.readlines()
        sample_file.close()
    return {"summary": summary}
from fastapi import FastAPI, Cookie, File, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Annotated 
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os, sqlite3
from search import initialise, search, get_all_departments
from pydantic import BaseModel
from durham_etheses_scraper import scrape, get_last_id, get_latest_id
from get_pdf_text import upload_pdf_texts_to_db_parallel
from gemini_ai_summariser import summarise_thesis
from auth import *
from create_admin import create_admin
import pandas as pd
import io

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
TOP_K = 10
DB_FOLDER = None
try:
    load_dotenv()
    DB_FOLDER = os.environ.get("DB_FOLDER")
except:
    DB_FOLDER = "./db"
if DB_FOLDER is None:
    DB_FOLDER = "./db"
DB_PATH = os.path.join(DB_FOLDER, "db.db")

df, index, ids, model = None, None, None, None
departments = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, index, ids, model, departments
    #startup code here
    print("Starting up...")
    df, index, ids, model = initialise(MODEL_NAME, INDEX_FILE, ID_FILE, DB_PATH)
    departments = get_all_departments(df)
    print("Startup complete.")
    yield
    #shutdown code here
    print("Shutting down...")


app = FastAPI()

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
# TODO: Make this not hang the server / multithreading?
# Updates the DB with new theses uploaded to Durham-Etheses, including PDF text extraction if full PDF is released.
async def update_db(token: Annotated[str | None, Cookie()] = None):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    last_id = get_last_id()
    latest_id = get_latest_id()
    print(f"Last ID in DB: {last_id}, Latest ID on site: {latest_id}")
    if last_id == latest_id:
        return {"message": "Database is already up to date"}
    for i in range(last_id + 1, latest_id + 1):
        result = scrape(i)
        if result == 0:
            print("Successfully added thesis with ID", i, "to the database.")
    upload_pdf_texts_to_db_parallel(DB_PATH=DB_PATH)
    return {"message": "Database updated successfully"}

@app.get("/summarise/{db_id}")
async def summarise(db_id: int):
    summary = summarise_thesis(db_id, DB_PATH=DB_PATH)
    return {"summary": summary}

@app.get("/login")
async def login(username: str, password: str):
    if check_creds(username, password):
        token = generate_token(username)
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/token")
async def test(token: Annotated[str | None, Cookie()] = None):
    print("Received token:", token)
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    return {"message": "Token is valid"}


class AdminUser(BaseModel):
    username: str
    password: str

@app.post("/create-admin")
async def create_admin_endpoint(admin_user: AdminUser, token: Annotated[str | None, Cookie()] = None):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    success = create_admin(admin_user.username, admin_user.password)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create admin user")
    return {"message": "Admin user created successfully"}


@app.post("/upload")
async def upload(file: Annotated[UploadFile, File()],
    titleField: Annotated[str | None, Form()],
    authorField: Annotated[str | None, Form()],
    yearField: Annotated[str | None, Form()],
    abstractField: Annotated[str | None, Form()],
    deptField: Annotated[str | None, Form()],
    keywordsField: Annotated[str | None, Form()],
    pdfUrlField: Annotated[str | None, Form()],
    urlField: Annotated[str | None, Form()],
    token: Annotated[str | None, Cookie()] = None
):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    # read uploaded csv file
    contents = await file.read()
    possible_fields = [titleField, authorField, yearField, abstractField, deptField, keywordsField, pdfUrlField, urlField]
    db_fields = ["title", "author", "year", "abstract", "department", "keywords", "pdf_url", "url", "pdf_text"]
    fields = [f for f in possible_fields if f is not None and f != ""]
    if len(fields) == 0:
        raise HTTPException(status_code=400, detail="At least one field must be specified")
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    df = df[fields]
    for i, field in enumerate(possible_fields):
        if field in fields:
            df.rename(columns={field: db_fields[i]}, inplace=True)
    con = sqlite3.connect("./db/db2.db")
    con.execute(
    '''
    CREATE TABLE IF NOT EXISTS "Thesis" (
    "id"	INTEGER NOT NULL,
    "title"	TEXT,
    "author"	TEXT,
    "abstract"	TEXT,
    "award"	NUMERIC,
    "keywords"	TEXT,
    "date"	NUMERIC,
    "faculty"	TEXT,
    "department"	TEXT,
    "url"	TEXT,
    "pdf_url"	TEXT,
    "pdf_text"	TEXT,
    PRIMARY KEY("id" AUTOINCREMENT)
    )
    '''
    )
    con.commit()
    for field in db_fields:
        if field not in df.columns:
            df[field] = None
    df.to_sql("Thesis", con, if_exists="append", index=False)
    con.close()
    print(df.keys())
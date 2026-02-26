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
# from index import build_index
from auth import *
from create_admin import create_admin
import pandas as pd
import io
import gc
import shutil
import time

load_dotenv()

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
TOP_K = 10
try:
    DB_PATH = os.environ.get("DB_PATH")
except:
    DB_PATH = "./db/db.db"
if DB_PATH is None:
    DB_PATH = "./db/db.db"

df, index, ids, model = None, None, None, None
departments = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, index, ids, model, departments, DB_PATH
    load_dotenv(override=True)
    try:
        DB_PATH = os.environ.get("DB_PATH")
    except:
        DB_PATH = "./db/db.db"
    if DB_PATH is None:
        DB_PATH = "./db/db.db"
    #startup code here
    print("Starting up...")
    df, index, ids, model = initialise(MODEL_NAME, INDEX_FILE, ID_FILE, DB_PATH)
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
    try:
        results = search(search_term.term, df, index, ids, model, search_term.count, search_term.fromYear, search_term.toYear, search_term.includeUnknown, authorField=search_term.authorField, deptCheckboxes=search_term.departments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
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
# TODO: This currently doesnt update the index so new theses wont come up in search results until index is rebuilt
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
async def upload(file: Annotated[UploadFile | None, File()] = None,
    indexFile: Annotated[UploadFile | None, File()] = None,
    idsFile: Annotated[UploadFile | None, File()] = None,
    titleField: Annotated[str | None, Form()] = None,
    authorField: Annotated[str | None, Form()] = None,
    yearField: Annotated[str | None, Form()] = None,
    abstractField: Annotated[str | None, Form()] = None,
    deptField: Annotated[str | None, Form()] = None,
    keywordsField: Annotated[str | None, Form()] = None,
    pdfUrlField: Annotated[str | None, Form()] = None,
    urlField: Annotated[str | None, Form()] = None,
    token: Annotated[str | None, Cookie()] = None
):
    global df, index, ids, model, departments, DB_PATH
    
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    if not file and not os.path.isfile(DB_PATH):
        raise HTTPException(status_code=400, detail="No database file provided and no existing database found")
    if not indexFile and not os.path.isfile(INDEX_FILE):
        raise HTTPException(status_code=400, detail="No index file provided and no existing index found")
    if not idsFile and not os.path.isfile(ID_FILE):
        raise HTTPException(status_code=400, detail="No IDs file provided and no existing IDs file found")


    if file:
        db_fields = ["title", "author", "date", "abstract", "department", "keywords", "pdf_url", "url", "pdf_text"]
        possible_fields = [titleField, authorField, yearField, abstractField, deptField, keywordsField, pdfUrlField, urlField]
        fields = [f for f in possible_fields if f is not None and f != ""]
        # read uploaded csv file
        if file.filename.endswith(".csv"):
            contents = await file.read()
            if len(fields) == 0:
                raise HTTPException(status_code=400, detail="At least one field must be specified")
            df2 = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            df2 = df2[fields]
            try:
                for i, field in enumerate(possible_fields):
                    if field in fields:
                        df2.rename(columns={field: db_fields[i]}, inplace=True)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing fields: {str(e)}")
            con = sqlite3.connect(DB_PATH)
            con.execute("DROP TABLE IF EXISTS Thesis")
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
                if field not in df2.columns:
                    df2[field] = None
            df2.to_sql("Thesis", con, if_exists="append", index=False)
            con.close()
            print(df2.keys())
        elif file.filename.endswith(".db"):
            try:
                if os.path.isfile("./db/temp.db"):
                    os.remove("./db/temp.db")
            except Exception as e:pass
            # if it's a db file, replace the existing db file with the uploaded one
            contents = await file.read()
            with open("./db/temp.db", "wb") as f:
                f.write(contents)
            await file.close()
            # check if the uploaded db has the correct schema
            with sqlite3.connect("./db/temp.db") as con:
                cur = con.execute("SELECT * FROM Thesis LIMIT 1")
                temp_fields = [field[0] for field in cur.description]
            db_fields = set(db_fields)
            if db_fields.issubset(set(temp_fields)):
                shutil.copyfile("./db/temp.db", DB_PATH)
                try:
                    os.remove("./db/temp.db")
                except Exception as e:pass
            else:
                if len(fields) == 0:
                    try:
                        os.remove("./db/temp.db")
                    except Exception as e:pass
                    raise HTTPException(status_code=400, detail=f"Uploaded database has incorrect schema. Expected fields: {db_fields}")
                else:
                    for field in fields:
                        try:
                            with sqlite3.connect("./db/temp.db") as con:
                                con.execute(f"ALTER TABLE Thesis RENAME COLUMN {field} TO {db_fields[possible_fields.index(field)]}")
                                con.commit()
                        except Exception as e:
                            os.remove("./db/temp.db")
                            raise HTTPException(status_code=400, detail=f"Error processing fields: {str(e)}")

                    for field in db_fields:
                        if field not in temp_fields:
                            with sqlite3.connect("./db/temp.db") as con:
                                con.execute(f"ALTER TABLE Thesis ADD COLUMN {field} TEXT")
                                con.commit()
                    shutil.copyfile("./db/temp.db", DB_PATH)

        else:
            raise HTTPException(status_code=400, detail="Invalid file type")
    if indexFile:
        contents = await indexFile.read()
        with open(INDEX_FILE, "wb") as f:
            f.write(contents)
    if idsFile:
        contents = await idsFile.read()
        with open(ID_FILE, "wb") as f:
            f.write(contents)
    df, index, ids, model = initialise(MODEL_NAME, INDEX_FILE, ID_FILE, DB_PATH)
    departments = get_all_departments(df)
    return {"message": "Files uploaded successfully"}
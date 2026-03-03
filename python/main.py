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
from index import build_index
from create_admin import delete_admin
from auth import *
from create_admin import create_admin
import pandas as pd
import io
import shutil

load_dotenv()

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INDEX_FILE = "durham_thesis.index"
ID_FILE = "durham_thesis_ids.npy"
TOP_K = 10
DB_PATH = os.environ.get("DB_PATH", "./db/db.db")
df, index, ids, model = None, None, None, None
departments = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, index, ids, model, departments, DB_PATH
    #startup code here

    print("Starting up...")
    if os.path.isfile(DB_PATH) and os.path.isfile(INDEX_FILE) and os.path.isfile(ID_FILE):
        df, index, ids, model = initialise(MODEL_NAME, INDEX_FILE, ID_FILE, DB_PATH)
        departments = get_all_departments(df)
    else:
        print("Warning: Database, index or IDs file not found. Please upload them through the admin panel.")
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
def search_users(search_term: SearchTerm):
    if search_term.term == "" and search_term.authorField == "" and len(search_term.departments) == 0:
        raise HTTPException(status_code=400, detail="At least one search parameter (term, authorField, departments) must be provided")
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
             "db_id": str(r[6]),
             "score": str(r[7])
             } for r in results]

@app.get("/departments")
async def get_departments():
    return departments

@app.post("/update-db")
# Updates the DB with new theses uploaded to Durham-Etheses, including PDF text extraction if full PDF is released.
def update_db(token: Annotated[str | None, Cookie()] = None):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    last_id = get_last_id()
    if last_id != -1:
        # Durham Etheses only.
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

@app.post("/index")
def rebuild_index(token: Annotated[str | None, Cookie()] = None):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    try:
        build_index(DB_PATH=DB_PATH, INDEX_FILE=INDEX_FILE, ID_FILE=ID_FILE)
    except NameError:
        print("CUDA is not available. Cannot rebuild index.")
        raise HTTPException(status_code=500, detail=f"Failed to build index: CUDA is not available on the server.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to build index: {str(e)}")
    return {"message": "Index rebuilt successfully"}

@app.get("/summarise/{db_id}")
def summarise(db_id: int):
    summary = summarise_thesis(db_id, DB_PATH=DB_PATH)
    return {"summary": summary}

@app.get("/login")
def login(username: str, password: str):
    if check_creds(username, password):
        token = generate_token(username)
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/token")
def test(token: Annotated[str | None, Cookie()] = None):
    print("Received token:", token)
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    return {"message": "Token is valid"}

@app.post("/logout")
def logout(token: Annotated[str | None, Cookie()] = None):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(key="token")
    return response

class AdminUser(BaseModel):
    username: str
    password: str

@app.post("/create-admin")
def create_admin_endpoint(admin_user: AdminUser, token: Annotated[str | None, Cookie()] = None):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    success = create_admin(admin_user.username, admin_user.password)
    if success == 400:
        raise HTTPException(status_code=400, detail="Bad request. Please ensure both username and password are provided.")
    elif success == 500:
        raise HTTPException(status_code=500, detail="Failed to create admin user")
    return {"message": "Admin user created successfully"}


@app.delete("/delete-admin")
def delete_admin_endpoint(username: str, token: Annotated[str | None, Cookie()] = None):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorised")
    status = delete_admin(username)
    if status == 404:
        raise HTTPException(status_code=404, detail="Admin user not found")
    elif status == 400:
        raise HTTPException(status_code=400, detail="Bad request. Please ensure a username is provided.")
    elif status != 200:
        raise HTTPException(status_code=500, detail="Failed to delete admin user")
    else:
        return {"message": "Admin user deleted successfully"}


async def upload_file(FILE_PATH, file: UploadFile):
    contents = await file.read()
    with open(FILE_PATH, "wb") as f:
        f.write(contents)
    await file.close()

@app.post("/upload")
async def upload(file: Annotated[UploadFile | None, File()] = None,
    indexFile: Annotated[UploadFile | None, File()] = None,
    idsFile: Annotated[UploadFile | None, File()] = None,
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
        # read uploaded csv file
        if file.filename.endswith(".csv"):
            contents = await file.read()
            df2 = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            valid_fields = [f for f in db_fields if f in df2.columns]
            if len(valid_fields) == 0:
                raise HTTPException(status_code=400, detail=f"CSV does not contain any required fields. Expected at least one of: {db_fields}")
            df2 = df2[valid_fields]
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
            try:
                with sqlite3.connect("./db/temp.db") as con:
                    try:
                        cur = con.execute("SELECT * FROM Thesis LIMIT 1")
                    except Exception as e:
                        raise HTTPException(status_code=400, detail=f"Uploaded database does not contain a 'Thesis' table with the correct schema: {str(e)}")
                    temp_fields = [field[0] for field in cur.description]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error reading uploaded database: {str(e)}")
            if set(db_fields).issubset(set(temp_fields)) or set(temp_fields).issubset(set(db_fields)):pass
            else:
                raise HTTPException(status_code=400, detail=f"Uploaded database does not contain the correct fields. Expected fields: {db_fields}. Uploaded database fields: {temp_fields}")

            for field in db_fields:
                if field not in temp_fields:
                    with sqlite3.connect("./db/temp.db") as con:
                        con.execute(f"ALTER TABLE Thesis ADD COLUMN {field} TEXT")
                        con.commit()
            shutil.copyfile("./db/temp.db", DB_PATH)

        else:
            raise HTTPException(status_code=400, detail="Invalid file type")
    if indexFile:
        if not indexFile.filename.endswith(".index"):
            raise HTTPException(status_code=400, detail="Index file must have .index extension")
        contents = await indexFile.read()
        upload_file(INDEX_FILE, indexFile)
    if idsFile:
        if not idsFile.filename.endswith(".npy"):
            raise HTTPException(status_code=400, detail="IDs file must have .npy extension")
        contents = await idsFile.read()
        upload_file(ID_FILE, idsFile)
    df, index, ids, model = initialise(MODEL_NAME, INDEX_FILE, ID_FILE, DB_PATH)
    departments = get_all_departments(df)
    return {"message": "Files uploaded successfully"}
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import sqlite3
load_dotenv()
app = FastAPI()
try:
    DB_PATH = os.getenv("DB_PATH")
except:
    DB_PATH = "./db/db.db"
DATABASE = DB_PATH

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

#endpoints
# @app.get("/")
# async def main():
#     return {"message": "This is a message from FastAPI"}

# Pydantic model for search term
class SearchTerm(BaseModel):
    term: str

@app.post("/search")
async def search_users(search: SearchTerm):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM Thesis WHERE title LIKE ?", ('%' + search.term + '%',))
    results = cursor.fetchall()
    conn.close()

    if not results:
        return []
    return [{"name": row[0]} for row in results]
import os
import tempfile
import sqlite3
import pytest
import types
import sys
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def test_db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # create mock Thesis table
    con = sqlite3.connect(path)
    con.execute("""
        CREATE TABLE Thesis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            award TEXT,
            author TEXT,
            abstract TEXT,
            department TEXT,
            date INTEGER,
            url TEXT,
            pdf_url TEXT,
            pdf_text TEXT
        )
    """)
    con.commit()
    con.close()

    yield path

    os.remove(path)

@pytest.fixture
def client(test_db_path, monkeypatch):

    fake_module = types.ModuleType("fake")
    sys.modules["torch"] = fake_module
    fake_st = types.ModuleType("sentence_transformers")

    class FakeSentenceTransformer:
        def __init__(self, *args, **kwargs):
            pass

        def encode(self, *args, **kwargs):
            return []

    fake_st.SentenceTransformer = FakeSentenceTransformer
    sys.modules["sentence_transformers"] = fake_st
    sys.modules["faiss"] = fake_module

    # Override env before app import so it uses mock DB
    monkeypatch.setenv("DB_PATH", test_db_path)

    # Import AFTER env patch
    import main

    # Mock external function calls
    # This test is just for the API endpoints. Test other functions separately

    # Mock initialisation
    monkeypatch.setattr(main, "initialise",
                        lambda *args, **kwargs: (None, None, None, None))

    # Mock departments (pretend this is the DB response instead of actually querying the DB)
    monkeypatch.setattr(main, "get_all_departments",
                        lambda df: ["Computer Science", "Maths"])

    # Mock auth
    monkeypatch.setattr(main, "verify_token",
                        lambda token: True)

    # Mock DB uploads, building indexes and generating AI summary
    monkeypatch.setattr(main, "upload_pdf_texts_to_db_parallel",
                        lambda DB_PATH=None: None)

    monkeypatch.setattr(main, "build_index",
                        lambda *args, **kwargs: None, raising=False)

    monkeypatch.setattr(main, "summarise_thesis",
                        lambda db_id, DB_PATH=None: "Fake summary")

    
    with TestClient(main.app) as c:
        yield c

def test_departments(client):
    response = client.get("/departments")
    assert response.status_code == 200
    # check response matches mock data
    assert response.json() == ["Computer Science", "Maths"]

def test_summarise_thesis(client):
    response = client.get("/summarise/1")
    assert response.status_code == 200
    assert response.json()["summary"] == "Fake summary"

def test_update_db(client, monkeypatch):
    import main
    monkeypatch.setattr(main, "get_latest_id",
                        lambda: 1)
    monkeypatch.setattr(main, "get_last_id",
                        lambda: 2)
    response = client.post("/update-db")
    assert response.status_code == 200
    assert response.json()["message"] == "Database updated successfully"

def test_upload_csv(client):

    csv_content = """title,author,abstract,department,date,pdf_url,pdf_text
Test Title,John Doe,Test abstract,Computer Science,2023,url,text
"""

    response = client.post(
        "/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Files uploaded successfully"
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
    # Mock torch import so it doesnt have a seizure
    sys.modules["torch"] = fake_module
    fake_st = types.ModuleType("sentence_transformers")
    # Mock SentenceTransformer class to avoid importError during testing.
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

def test_update_db_authenticated(client, monkeypatch):
    import main
    # Mock get_latest_id and get_last_id to simulate DB needing update
    monkeypatch.setattr(main, "get_latest_id",
                        lambda: 1)
    monkeypatch.setattr(main, "get_last_id",
                        lambda: 2)
    monkeypatch.setattr(main, "verify_token",
                        lambda token: True)
    response = client.post("/update-db")
    # Check response is success and message is correct
    assert response.status_code == 200
    assert response.json()["message"] == "Database updated successfully"

def test_update_db_already_up_to_date(client, monkeypatch):
    import main
    # Mock get_latest_id and get_last_id to simulate DB already up to date
    monkeypatch.setattr(main, "get_latest_id",
                        lambda: 1)
    monkeypatch.setattr(main, "get_last_id",
                        lambda: 1)
    monkeypatch.setattr(main, "verify_token",
                        lambda token: True)
    response = client.post("/update-db")
    # Check response is success and message is correct
    assert response.status_code == 200
    assert response.json()["message"] == "Database is already up to date"

def test_update_db_unauthenticated(client, monkeypatch):
    import main
    # Mock unauthenticated user trying to update DB. Should return 401 Unauthorised
    monkeypatch.setattr(main, "get_latest_id",
                        lambda: 1)
    monkeypatch.setattr(main, "get_last_id",
                        lambda: 2)
    monkeypatch.setattr(main, "verify_token",
                        lambda token: False)
    response = client.post("/update-db")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorised"

def test_rebuild_index_authenticated(client, monkeypatch):
    import main
    # Mock authenticated user trying to rebuild index. Should return success message
    monkeypatch.setattr(main, "verify_token",
                        lambda token: True)
    response = client.post("/index")
    assert response.status_code == 200
    assert response.json()["message"] == "Index rebuilt successfully"

def test_rebuild_index_unauthenticated(client, monkeypatch):
    import main
    # Mock unauthenticated user trying to rebuild index. Should return 401 Unauthorised
    monkeypatch.setattr(main, "verify_token",
                        lambda token: False)
    response = client.post("/index")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorised"

def test_upload_csv_valid(client):

    csv_content = """title,author,abstract,department,date,pdf_url,pdf_text
Test Title,John Doe,Test abstract,Computer Science,2023,url,text
"""

    response = client.post(
        "/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Files uploaded successfully"

def test_upload_unauthenticated(client, monkeypatch):
    import main
    # Mock unauthenticated user trying to upload CSV. Should return 401 Unauthorised
    monkeypatch.setattr(main, "verify_token",
                        lambda token: False)
    csv_content = """title,author,abstract,department,date,pdf_url,pdf_text
Test Title,John Doe,Test abstract,Computer Science,2023,url,text
"""

    response = client.post(
        "/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorised"

def test_upload_csv_invalid(client):
    # CSV with invalid file type (txt instead of csv)
    csv_content = """title,author,abstract,department,date,pdf_url,pdf_text
Test Title,John Doe,Test abstract,Computer Science,2023,url,text
"""

    response = client.post(
        "/upload",
        files={"file": ("test.txt", csv_content, "text/plain")},  # Invalid file extension
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type"

def test_upload_csv_incorrect_format(client):
    # Incorrect fields for the CSV
    csv_content = """completely,wrong,fields,for,testing,purposes
Test Title,John Doe,Test abstract,Computer Science,2023,url
"""

    response = client.post(
        "/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 400

#TODO: upload DB file tests

def test_upload_index_valid(client, monkeypatch):
    import main
    # Mock authenticated user trying to upload index. Should return success message
    monkeypatch.setattr(main, "verify_token",
                        lambda token: True)
    content = "Fake index content"
    response = client.post(
        "/upload",
        files={"indexFile": ("test.index", content, "")},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Files uploaded successfully"

def test_upload_index_invalid(client, monkeypatch):
    import main
    # Mock authenticated user trying to upload invalid index file. Should return error message
    monkeypatch.setattr(main, "verify_token",
                        lambda token: True)
    content = "Fake index content"
    response = client.post(
        "/upload",
        files={"indexFile": ("test.invalid", content, "")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Index file must have .index extension"

def test_upload_ids_valid(client, monkeypatch):
    import main
    # Mock authenticated user trying to upload IDs file. Should return success message
    monkeypatch.setattr(main, "verify_token",
                        lambda token: True)
    content = "Fake IDs content"
    response = client.post(
        "/upload",
        files={"idsFile": ("test.npy", content, "")},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Files uploaded successfully"

def test_upload_ids_invalid(client, monkeypatch):
    import main
    # Mock authenticated user trying to upload invalid IDs file. Should return error message
    monkeypatch.setattr(main, "verify_token",
                        lambda token: True)
    content = "Fake IDs content"
    response = client.post(
        "/upload",
        files={"idsFile": ("test.invalid", content, "")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "IDs file must have .npy extension"
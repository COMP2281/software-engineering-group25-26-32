import os
import tempfile
import sqlite3
import pytest
import types
import sys
import json
import pymupdf

@pytest.fixture(scope="session")
def test_db_path():
    # Create temporary db
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # create mock Thesis table
    con = sqlite3.connect(path)
    con.execute("""
        CREATE TABLE Thesis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            award TEXT,
            keywords TEXT,
            author TEXT,
            abstract TEXT,
            faculty TEXT,
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
    # Delete temp db after tests complete
    os.remove(path)

@pytest.fixture
def get_pdf_text(test_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", test_db_path)
    # Import AFTER env patch
    import get_pdf_text
    yield get_pdf_text

# TESTS FOR get_unprocessed_ids

def test_get_unprocessed_ids(get_pdf_text, test_db_path):
    # Insert test data
    con = sqlite3.connect(test_db_path)
    con.execute("INSERT INTO Thesis (pdf_url) VALUES ('http://example.com/test1.pdf')")
    con.execute("INSERT INTO Thesis (pdf_url, pdf_text) VALUES ('http://example.com/test2.pdf', 'Some text')")
    con.commit()
    con.close()

    ids = get_pdf_text.get_unprocessed_ids(DB_PATH=test_db_path)
    assert len(ids) == 1
    assert ids[0] == 1

def test_get_unprocessed_ids_malformed_pdf_url(get_pdf_text, test_db_path):
    con = sqlite3.connect(test_db_path)
    # Clear existing data from previous tests
    con.execute("DELETE FROM Thesis") 
    con.commit()
    # Insert test data with malformed URL
    con.execute("INSERT INTO Thesis (pdf_url) VALUES ('not_a_url')")
    con.commit()
    con.close()

    ids = get_pdf_text.get_unprocessed_ids(DB_PATH=test_db_path)
    assert len(ids) == 0


# TESTS FOR pdf_urls_from_id_list

def test_pdf_urls_from_id_list(get_pdf_text, test_db_path):
    con = sqlite3.connect(test_db_path)
    # Clear existing data from previous tests
    con.execute("DELETE FROM Thesis") 
    con.commit()
    # Insert test data
    con.execute("INSERT INTO Thesis (title, date, pdf_url) VALUES ('Test Thesis 1', '2026', 'http://example.com/test1.pdf')")
    con.execute("INSERT INTO Thesis (title, date, pdf_url) VALUES ('Test Thesis 2', '2024', 'http://example.com/test2.pdf')")
    rows =con.execute("SELECT id FROM Thesis").fetchall()
    ids = [row[0] for row in rows]

    con.commit()
    con.close()
    
    rows = get_pdf_text.pdf_urls_from_id_list([ids[0], ids[1]], DB_PATH=test_db_path)
    assert len(rows) == 2
    assert rows[0][0] == ids[0]
    assert rows[0][1] == "Test Thesis 1"
    assert rows[0][2] == 2026
    assert rows[0][3] == "http://example.com/test1.pdf"
    assert rows[1][0] == ids[1]
    assert rows[1][1] == "Test Thesis 2"
    assert rows[1][2] == 2024
    assert rows[1][3] == "http://example.com/test2.pdf"

def test_pdf_urls_from_id_list_nonexistent_id(get_pdf_text, test_db_path):
    con = sqlite3.connect(test_db_path)
    # Clear existing data from previous tests
    con.execute("DELETE FROM Thesis") 
    con.commit()
    con.close()

    rows = get_pdf_text.pdf_urls_from_id_list([999], DB_PATH=test_db_path)
    assert len(rows) == 0

# TESTS FOR is_garbage

def test_is_garbage(get_pdf_text):
    assert get_pdf_text.is_garbage("normal text.") == False
    assert get_pdf_text.is_garbage("!@#$%^&*()_+") == True
    assert get_pdf_text.is_garbage(".......") == False # contents pages have a lot of dots but arent garbage
    assert get_pdf_text.is_garbage("some, but not all, garbage !@#$%") == False


# TESTS FOR pdf_to_txt_json

def test_pdf_to_txt_json(get_pdf_text, test_db_path, monkeypatch):
    monkeypatch.setattr(get_pdf_text, "read_pdf_from_url", lambda url:pymupdf.Document(filename="./tests/sample/sample.pdf", filetype="pdf"))
    monkeypatch.setattr(get_pdf_text, "is_garbage", lambda text: False) # disable garbage detection to force use of get_text() instead of OCR for testing
    monkeypatch.setattr(get_pdf_text, "pdf_urls_from_id_list", lambda ids, DB_PATH=None: [(ids[0], "Placeholder", "Placeholder", "http://example.com/test.pdf")])
    text_json = get_pdf_text.pdf_to_txt_json(1, DB_PATH=test_db_path)
    assert type(text_json) == str
    assert "A very interesting thesis" in text_json
    assert "\"source\": \"http://example.com/test.pdf\"" in text_json
    assert "\"page\": 1" in text_json


# TESTS FOR doc_text_to_db

def test_doc_text_to_db(get_pdf_text, test_db_path):
    con = sqlite3.connect(test_db_path)
    # Clear existing data from previous tests
    con.execute("DELETE FROM Thesis") 
    con.commit()
    # Insert test data
    con.execute("INSERT INTO Thesis (title) VALUES ('Test Thesis')")
    doc_id = con.execute("SELECT id FROM Thesis WHERE title = 'Test Thesis'").fetchone()[0]
    con.commit()
    con.close()

    get_pdf_text.doc_text_to_db(doc_id, "Extracted text", DB_PATH=test_db_path)

    con = sqlite3.connect(test_db_path)
    pdf_text = con.execute("SELECT pdf_text FROM Thesis WHERE id = ?", (doc_id,)).fetchone()[0]
    con.close()
    assert pdf_text == "Extracted text"
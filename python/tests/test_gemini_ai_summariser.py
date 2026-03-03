import os
import tempfile
import sqlite3
import pytest
import types
import sys
import json

# INITIALISE MOCK DB

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
def gemini_ai_summariser(test_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", test_db_path)
    fake_gemini = types.ModuleType("google.genai")
    # Mock gemini.Client and gemini.models.Model to avoid making actual API calls
    class FakeModel:
        def generate_content(self, *args, **kwargs):
            return types.SimpleNamespace(text="Fake summary")
    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.models = FakeModel() 
    fake_gemini.Client = FakeClient
    sys.modules["google.genai"] = fake_gemini
    # Import AFTER env patch
    import gemini_ai_summariser

    yield gemini_ai_summariser


# TESTS FOR load_pages()

def test_load_pages(gemini_ai_summariser):
    # Insert mock thesis with 2 pages into db
    con = sqlite3.connect(gemini_ai_summariser.DB_PATH)
    pdf_text = json.dumps({"metadata": {"page": 1}, "text": "Page 1 text"}) + "\n" + json.dumps({"metadata": {"page": 2}, "text": "Page 2 text"})
    con.execute("INSERT INTO Thesis (title,pdf_text) VALUES (?,?)", ("Test Thesis", pdf_text))
    doc_id = con.execute("SELECT id FROM Thesis WHERE title = 'Test Thesis'").fetchone()[0]
    con.commit()
    con.close()

    pages = gemini_ai_summariser.load_pages(doc_id, gemini_ai_summariser.DB_PATH)
    assert "PDF PAGE 1: \n Page 1 text" in pages
    assert "PDF PAGE 2: \n Page 2 text" in pages
    assert pages.find("PDF PAGE 1: \n Page 1 text") < pages.find("PDF PAGE 2: \n Page 2 text") # check page order is correct
    assert type(pages) == str

def test_load_pages_no_pages(gemini_ai_summariser):
    # Insert mock thesis with no pages into db
    con = sqlite3.connect(gemini_ai_summariser.DB_PATH)
    con.execute("INSERT INTO Thesis (title,pdf_text) VALUES (?,?)", ("Test Thesis No Pages", ""))
    doc_id = con.execute("SELECT id FROM Thesis WHERE title = 'Test Thesis No Pages'").fetchone()[0]
    con.commit()
    con.close()

    pages = gemini_ai_summariser.load_pages(doc_id, gemini_ai_summariser.DB_PATH)
    assert pages == ""

def test_load_pages_invalid_id(gemini_ai_summariser):
    pages = gemini_ai_summariser.load_pages(9999, gemini_ai_summariser.DB_PATH)
    assert pages == ""


# TESTS FOR summarise_thesis()

def test_summarise_thesis(gemini_ai_summariser, monkeypatch):
    monkeypatch.setattr(gemini_ai_summariser, "load_pages", lambda doc_id, DB_PATH=None: "Fake pages")
    summary = gemini_ai_summariser.summarise_thesis(DOC_ID=1, DB_PATH=gemini_ai_summariser.DB_PATH)
    assert summary == "Fake summary"

def test_summarise_thesis_with_query(gemini_ai_summariser, monkeypatch):
    monkeypatch.setattr(gemini_ai_summariser, "load_pages", lambda doc_id, DB_PATH=None: "Fake pages")
    summary = gemini_ai_summariser.summarise_thesis(DOC_ID=1, DB_PATH=gemini_ai_summariser.DB_PATH)
    assert summary == "Fake summary"

def test_summarise_thesis_no_pages(gemini_ai_summariser, monkeypatch):
    monkeypatch.setattr(gemini_ai_summariser, "load_pages", lambda doc_id, DB_PATH=None: "")
    summary = gemini_ai_summariser.summarise_thesis(DOC_ID=1, DB_PATH=gemini_ai_summariser.DB_PATH)
    assert summary == "Full text not available for this thesis"

def test_summarise_thesis_strips_garbage(gemini_ai_summariser, monkeypatch):
    # Check that <html> etc tags that Gemini likes to add are removed
    fake_gemini = types.ModuleType("google.genai")
    # Mock gemini.Client and gemini.models.Model to avoid making actual API calls
    class FakeModel:
        def generate_content(self, *args, **kwargs):
            return types.SimpleNamespace(text="<html>Fake summary</html>")
    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.models = FakeModel() 
    fake_gemini.Client = FakeClient
    monkeypatch.setattr(gemini_ai_summariser, "gemini", fake_gemini)
    monkeypatch.setattr(gemini_ai_summariser, "load_pages", lambda doc_id, DB_PATH=None: "Fake Pages")
    summary = gemini_ai_summariser.summarise_thesis(DOC_ID=1)
    assert summary == "Fake summary"
    class FakeModel:
        def generate_content(self, *args, **kwargs):
            return types.SimpleNamespace(text="```htmlFake summary```")
        class FakeClient:
            def __init__(self, *args, **kwargs):
                self.models = FakeModel() 
    fake_gemini.Client = FakeClient
    monkeypatch.setattr(gemini_ai_summariser, "gemini", fake_gemini)
    summary = gemini_ai_summariser.summarise_thesis(DOC_ID=1)
    assert summary == "Fake summary"
    class FakeModel:
        def generate_content(self, *args, **kwargs):
            return types.SimpleNamespace(text="<code>Fake summary</code>")
        class FakeClient:
            def __init__(self, *args, **kwargs):
                self.models = FakeModel() 
    fake_gemini.Client = FakeClient
    monkeypatch.setattr(gemini_ai_summariser, "gemini", fake_gemini)
    summary = gemini_ai_summariser.summarise_thesis(DOC_ID=1)
    assert summary == "Fake summary"
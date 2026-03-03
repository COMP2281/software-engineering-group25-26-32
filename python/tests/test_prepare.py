import os
import tempfile
import sqlite3
import pytest

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
def prepare(test_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", test_db_path)

    # Import AFTER env patch
    import prepare

    yield prepare


# TESTS FOR normalise()

def test_normalise_str(prepare):
    assert prepare.normalise("  ew, whitespace?  ") == "ew, whitespace?"
    assert prepare.normalise("This   is a   test.") == "This is a test."
    assert prepare.normalise("!!!") == "!"

def test_normalise_non_str(prepare):
    assert prepare.normalise(None) == ""
    assert prepare.normalise(67) == ""
    assert prepare.normalise(["list", "of", "strings"]) == ""


# TESTS FOR load_theses()

def test_load_theses(prepare, test_db_path):
    # Add test data to mock database
    con = sqlite3.connect(test_db_path)
    con.execute("INSERT INTO Thesis (title, author, date, abstract, department) VALUES (?, ?, ?, ?, ?)", ("I Am Smart: a Thesis", "piggypiggyyoinkyoink", 2026, "This thesis explores why I am smart", "Computer Science"))
    con.commit()
    con.close()

    df = prepare.load_theses(test_db_path)
    assert len(df) == 1
    assert df.iloc[0]["title"] == "I Am Smart: a Thesis"
    assert df.iloc[0]["author"] == "piggypiggyyoinkyoink"
    assert df.iloc[0]["year"] == "2026"
    assert df.iloc[0]["abstract"] == "This thesis explores why I am smart"
    assert df.iloc[0]["department"] == "Computer Science"


# TESTS FOR build_text()

def test_build_text(prepare):
    row = {
        "title": "I Am Smart: a Thesis",
        "abstract": "This thesis explores why I am smart",
        "department": "Computer Science"
    }
    text = prepare.build_text(row)
    assert text == "I Am Smart: a Thesis. This thesis explores why I am smart. Department: Computer Science"

    row_no_abstract = {
        "title": "I Am Smart: a Thesis",
        "department": "Computer Science"
    }
    text = prepare.build_text(row_no_abstract)
    assert text == "I Am Smart: a Thesis. Department: Computer Science"

    row_no_department = {
        "title": "I Am Smart: a Thesis",
        "abstract": "This thesis explores why I am smart"
    }
    text = prepare.build_text(row_no_department)
    assert text == "I Am Smart: a Thesis. This thesis explores why I am smart"

    row_no_title = {
        "abstract": "This thesis explores why I am smart",
        "department": "Computer Science"
    }
    text = prepare.build_text(row_no_title)
    assert text == "This thesis explores why I am smart. Department: Computer Science"
import os
import tempfile
import sqlite3
import pytest
import types
import sys
import json
from unittest.mock import Mock

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
            keywords TEXT,
            award TEXT,
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
def durham_etheses_scraper(test_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", test_db_path)


    # Import AFTER env patch
    import durham_etheses_scraper
    # Mock the actual web requests to durham e-theses
    monkeypatch.setattr(durham_etheses_scraper, "url_to_str", lambda url: open("./tests/sample/test_durham_etheses_scraper_example.html").read() if "cgi/latest" not in url else open("./tests/sample/test_durham_etheses_scraper_latest.html").read())

    yield durham_etheses_scraper


# TESTS FOR get_table_data()

def test_get_table_data(durham_etheses_scraper):
    mystr = open("./tests/sample/test_durham_etheses_scraper_example.html").read()
    award, faculty, department = durham_etheses_scraper.get_table_data(mystr)
    assert award == "AWARD"
    assert faculty == "Science"
    assert department == "Computer Science"

def test_get_table_data_missing(durham_etheses_scraper):
    mystr = "nothing to see here"
    award, faculty, department = durham_etheses_scraper.get_table_data(mystr)
    assert award is None
    assert faculty is None
    assert department is None


# TESTS FOR get_metadata()

def test_get_metadata(durham_etheses_scraper):
    mystr = open("./tests/sample/test_durham_etheses_scraper_example.html").read()
    title, author, abstract, award, keywords, date, faculty, dept, pdf_url = durham_etheses_scraper.get_metadata(mystr)
    assert title == "EXAMPLE TITLE"
    assert author == "EXAMPLE AUTHOR"
    assert abstract == "EXAMPLE_ABSTRACT"
    assert award == "AWARD"
    assert keywords == "KEYWORD1, KEYWORD2, KEYWORD3"
    assert date == "2026"
    assert faculty == "Science"
    assert dept == "Computer Science"
    assert pdf_url == "http://etheses.dur.ac.uk/EXAMPLE_URL.pdf"

def test_get_metadata_missing(durham_etheses_scraper):
    mystr = "nothing to see here"
    title, author, abstract, award, keywords, date, faculty, dept, pdf_url = durham_etheses_scraper.get_metadata(mystr)
    assert title is None
    assert author is None
    assert abstract is None
    assert award is None
    assert keywords == ""
    assert date is None
    assert faculty is None
    assert dept is None
    assert pdf_url is None


# TESTS FOR write_to_db()

def test_write_to_db(durham_etheses_scraper, test_db_path):
    durham_etheses_scraper.write_to_db("TITLE", "AUTHOR", "ABSTRACT", "AWARD", "KEYWORD1, KEYWORD2", "2026", "Science", "Computer Science", "https://etheses.dur.ac.uk/EXAMPLE_URL/", "http://etheses.dur.ac.uk/EXAMPLE_URL.pdf")
    con = sqlite3.connect(test_db_path)
    cur = con.cursor()
    cur.execute("SELECT title, author, abstract, award, keywords, date, faculty, department, url, pdf_url FROM Thesis WHERE id=1")
    row = cur.fetchone()
    con.close()
    assert row == ("TITLE", "AUTHOR", "ABSTRACT", "AWARD", "KEYWORD1, KEYWORD2", 2026, "Science", "Computer Science", "https://etheses.dur.ac.uk/EXAMPLE_URL/", "http://etheses.dur.ac.uk/EXAMPLE_URL.pdf")

def test_write_to_db_all_none(durham_etheses_scraper, test_db_path):
    # Test that if all fields are None, nothing is written to the db
    durham_etheses_scraper.write_to_db(None, None, None, None, None, None, None, None, None, None)
    con = sqlite3.connect(test_db_path)
    cur = con.cursor()
    cur.execute("SELECT title, author, abstract, award, keywords, date, faculty, department, url, pdf_url FROM Thesis")
    rows = cur.fetchall()
    con.close()
    for row in rows:
        assert row != (None, None, None, None, None, None, None, None, None, None)


# tests for scrape()

# OUTDATED TEST - Durham-Etheses website has been reformatted
# def test_scrape(durham_etheses_scraper, test_db_path, monkeypatch):
#     # Mock the actual web requests to durham e-theses
#     monkeypatch.setattr(durham_etheses_scraper, "url_to_str", lambda url: open("./tests/sample/test_durham_etheses_scraper_example.html").read() if "cgi/latest" not in url else open("./tests/sample/test_durham_etheses_scraper_latest.html").read())

#     # Call the scrape function
#     result = durham_etheses_scraper.scrape("EXAMPLE_URL")

#     # Assert that the function returned 0 (success)
#     assert result == 0

#     # Assert that the data was written to the database
#     con = sqlite3.connect(test_db_path)
#     cur = con.cursor()
#     cur.execute("SELECT title, author, abstract, award, keywords, date, faculty, department, url, pdf_url FROM Thesis ORDER BY id DESC LIMIT 1")
#     row = cur.fetchone()
#     con.close()
#     assert row == ("EXAMPLE TITLE", "EXAMPLE AUTHOR", "EXAMPLE_ABSTRACT", "AWARD", "KEYWORD1, KEYWORD2, KEYWORD3", 2026, "Science", "Computer Science", "https://etheses.dur.ac.uk/EXAMPLE_URL/", "http://etheses.dur.ac.uk/EXAMPLE_URL.pdf")

def test_scrape_nonexistent(durham_etheses_scraper, monkeypatch):
    # Mock the actual web requests to durham e-theses to return a page that indicates the thesis doesn't exist
    monkeypatch.setattr(durham_etheses_scraper, "url_to_str", lambda url: None)
    mock_db_write = Mock()
    durham_etheses_scraper.write_to_db = mock_db_write # mock write_to_db to check it is not called when thesis is removed
    
    # Call the scrape function with a non-existent thesis id
    result = durham_etheses_scraper.scrape("NONEXISTENT_URL")

    # Assert that write_to_db was not called since the thesis doesn't exist
    mock_db_write.assert_not_called()
    # Assert that the function returned 1 (indicating thesis doesn't exist)
    assert result == 1

def test_scrape_removed(durham_etheses_scraper, monkeypatch):
    # Mock the actual web requests to durham e-theses to return a page that indicates the thesis has been removed
    monkeypatch.setattr(durham_etheses_scraper, "url_to_str", lambda url: '<HTML stuffs> <p>You seem to be attempting to access an item that has been removed from the repository.</p> <more html stuffs>')
    mock_db_write = Mock()
    durham_etheses_scraper.write_to_db = mock_db_write # mock write_to_db to check it is not called when thesis is removed
    # Call the scrape function with a removed thesis id
    result = durham_etheses_scraper.scrape("REMOVED_URL")

    # Assert that write_to_db was not called since the thesis no longer exists
    mock_db_write.assert_not_called()
    # Assert that the function returned 1 (indicating thesis doesn't exist)
    assert result == 1


# TESTS FOR get_latest_id()

def test_get_latest_id(durham_etheses_scraper, monkeypatch):
    # Mock the actual web requests to durham e-theses
    monkeypatch.setattr(durham_etheses_scraper, "url_to_str", lambda url: open("./tests/sample/test_durham_etheses_scraper_latest.html").read())
    latest_id = durham_etheses_scraper.get_latest_id()
    assert latest_id == 1234567

def test_get_latest_id_no_results(durham_etheses_scraper, monkeypatch):
    # Mock the actual web requests to durham e-theses to return garbage
    monkeypatch.setattr(durham_etheses_scraper, "url_to_str", lambda url: "nothing to see here")
    latest_id = durham_etheses_scraper.get_latest_id()
    assert latest_id is None


# TESTS FOR get_last_id()

def test_get_last_id(durham_etheses_scraper, test_db_path):
    # Add test data to mock database
    con = sqlite3.connect(test_db_path)
    con.execute("INSERT INTO Thesis (url) VALUES (?)", ("https://etheses.dur.ac.uk/6767/",))
    con.commit()
    con.close()

    last_id = durham_etheses_scraper.get_last_id(test_db_path)
    assert last_id == 6767

def test_get_last_id_empty_db(durham_etheses_scraper, test_db_path):
    con = sqlite3.connect(test_db_path)
    con.execute("DELETE FROM Thesis")
    con.commit()
    con.close()
    last_id = durham_etheses_scraper.get_last_id(test_db_path)
    assert last_id == 0
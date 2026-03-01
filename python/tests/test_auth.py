import os
import sys
import tempfile
import sqlite3
import bcrypt
import pytest
from unittest.mock import Mock


@pytest.fixture(scope="session")
def test_user_db_path():
    # Create temporary db
    f, path = tempfile.mkstemp(suffix=".db")
    os.close(f)
    # Create mock Admin table and add test user
    con = sqlite3.connect(path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS Admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    con.commit()
    # Add test user with username "TEST" and password "password"
    password = bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()) # has password for testing login functionality
    con.execute("INSERT INTO Admin (username, password) VALUES (?, ?)", ("TEST", password))
    con.commit()
    con.close()
    yield path
    # Delete temp db after tests complete
    os.remove(path)

@pytest.fixture
def auth(test_user_db_path, monkeypatch):
    monkeypatch.setenv("USERS_DB_PATH", test_user_db_path)

    # Import AFTER env patch
    import auth

    yield auth


# TESTS FOR check_creds()

def test_check_creds_valid(auth):
    assert auth.check_creds("TEST", "password") == True

def test_check_creds_invalid_username(auth):
    assert auth.check_creds("INVALID", "password") == False

def test_check_creds_invalid_password(auth):
    assert auth.check_creds("TEST", "wrongpassword") == False

def test_check_creds_invalid_both(auth):
    assert auth.check_creds("INVALID", "wrongpassword") == False

def test_check_creds_empty(auth):
    assert auth.check_creds("", "") == False


# TESTS FOR generate_token() and verify_token()

def test_generate_and_verify_token(auth):
    token = auth.generate_token("TEST")
    assert isinstance(token, str)
    username = auth.verify_token(token)
    assert username == "TEST"

def test_verify_token_invalid(auth):
    assert auth.verify_token("invalidtoken") is None

def test_verify_token_modified(auth):
    token = auth.generate_token("TEST")
    tampered_token = token + "garbage"
    assert auth.verify_token(tampered_token) is None
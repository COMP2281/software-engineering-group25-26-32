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
def client(test_user_db_path, monkeypatch):
    monkeypatch.setenv("USERS_DB_PATH", test_user_db_path)

    # Import AFTER env patch
    import create_admin

    yield create_admin


def test_create_admin_success(client):
    # Test creating a new admin user
    result = client.create_admin("NEW_ADMIN", "newpassword")
    assert result == True

    # Check that the new admin user was added to the mock database
    con = sqlite3.connect(client.DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT username FROM Admin WHERE username = ?", ("NEW_ADMIN",))
    row = cur.fetchone()
    cur.close()
    con.close()
    assert row is not None
    assert row[0] == "NEW_ADMIN"

def test_create_admin_duplicate_username(client):
    # Test creating an admin user with a duplicate username
    result = client.create_admin("TEST", "anotherpassword")
    assert result == False

def test_create_admin_missing_fields(client):
    # Test creating an admin user with missing username
    result = client.create_admin("", "password")
    assert result == False

    # Test creating an admin user with missing password
    result = client.create_admin("USERNAME", "")
    assert result == False

def test_handle_valid_cli_arguments(client, monkeypatch):
    # Mock create_admin so we can just test the passing of CLI arguments
    # We already tested create_admin itself in the previous tests
    mock_create_admin = Mock(return_value=True)
    monkeypatch.setattr(client, "create_admin", mock_create_admin)
    monkeypatch.setattr(
        sys,
        "argv",
        ["create-admin.py", "NEW_ADMIN_2", "password2", "--db", os.environ.get("USERS_DB_PATH", None)]
    )
    result = client.main()
    assert result == True
    # check that create_admin was called with the correct arguments
    mock_create_admin.assert_called_once_with("NEW_ADMIN_2", "password2", os.environ.get("USERS_DB_PATH", None))

def test_handle_missing_cli_arguments(client, monkeypatch):
    # Test both missing arguments
    monkeypatch.setattr(
        sys,
        "argv",
        ["create-admin.py", "--db", os.environ.get("USERS_DB_PATH", None)]
    )
    with pytest.raises(SystemExit):
        result = client.main()
        assert result == False

    # Test missing password argument
    monkeypatch.setattr(
        sys,
        "argv",
        ["create-admin.py", "USERNAME_ONLY", "--db", os.environ.get("USERS_DB_PATH", None)]
    )
    with pytest.raises(SystemExit):
        result = client.main()
        assert result == False
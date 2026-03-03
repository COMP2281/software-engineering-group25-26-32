import argparse, sqlite3, os, bcrypt
from dotenv import load_dotenv
load_dotenv()
DB_PATH = os.environ.get("USERS_DB_PATH", "./db/users.db")

def create_admin(username, password, DB_PATH=DB_PATH):
    if not username or not password or username.strip() == "" or password.strip() == "":
        print("Error: Both username and password are required.")
        return 400
    try:
        conn = sqlite3.connect(DB_PATH)
    except:
        if not os.path.exists(os.path.dirname(DB_PATH)):
            print(f"Error: Directory for database does not exist at {os.path.dirname(DB_PATH)}. Please create the directory and try again.")
        else:
            print(f"Error: Could not connect to database at {DB_PATH}. Please check the path and try again.")
        return 500
    cur = conn.cursor()

    # Create the Admin table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # Check if the username already exists
    cur.execute("SELECT id FROM Admin WHERE username = ?", (username,))
    if cur.fetchone() is not None:
        print(f"Error: Admin user '{username}' already exists.")
        cur.close()
        conn.close()
        return 400
    # Insert the new admin user
    try:
        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO Admin (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print(f"Admin user '{username}' created successfully.")
        return 200
    except sqlite3.IntegrityError:
        print(f"Error: Admin user '{username}' already exists.")
        return 400
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return 500
    finally:
        cur.close()
        conn.close()

def delete_admin(username, DB_PATH=DB_PATH):
    if not username or username.strip() == "":
        print("Error: Username is required.")
        return 400
    try:
        conn = sqlite3.connect(DB_PATH)
    except:
        if not os.path.exists(os.path.dirname(DB_PATH)):
            print(f"Error: Directory for database does not exist at {os.path.dirname(DB_PATH)}. Please create the directory and try again.")
        else:
            print(f"Error: Could not connect to database at {DB_PATH}. Please check the path and try again.")
        return 400
    cur = conn.cursor()
    cur.execute("DELETE FROM Admin WHERE username = ?", (username,))
    if cur.rowcount == 0:
        print(f"Error: Admin user '{username}' does not exist.")
        cur.close()
        conn.close()
        return 404
    conn.commit()
    print(f"Admin user '{username}' deleted successfully.")
    cur.close()
    conn.close()
    return 200

def main():
    load_dotenv()
    DB_PATH = os.environ.get("USERS_DB_PATH", "./db/users.db")
    parser = argparse.ArgumentParser(description="Create an admin user for the thesis search application.")
    parser.add_argument("username", type=str, help="The username for the admin user.")
    parser.add_argument("password", type=str, help="The password for the admin user.")
    parser.add_argument("--db", type=str, default=DB_PATH, help="Path to the SQLite user database file.")
    args = parser.parse_args()
    if not args.username or not args.password:
        print("Error: Both username and password are required.")
        return False
    if args.db:
        DB_PATH = args.db
    return create_admin(args.username, args.password, DB_PATH)

if __name__ == "__main__":
    main()
import argparse, sqlite3, os, bcrypt
from dotenv import load_dotenv
load_dotenv()
try:
    DB_PATH = os.environ.get("USERS_DB_PATH")
except:
    DB_PATH = "./db/users.db"
if DB_PATH is None:
    DB_PATH = "./db/users.db"

def create_admin(username, password, DB_PATH=DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create the Admin table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Insert the new admin user
    try:
        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO Admin (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print(f"Admin user '{username}' created successfully.")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Admin user '{username}' already exists.")
        return False
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Usage: python create-admin.py <username> <password>
    parser = argparse.ArgumentParser(description="Create an admin user for the thesis search application.")
    parser.add_argument("username", type=str, help="The username for the admin user.")
    parser.add_argument("password", type=str, help="The password for the admin user.")
    parser.add_argument("--db", type=str, default=DB_PATH, help="Path to the SQLite user database file.")
    args = parser.parse_args()
    if not args.username or not args.password:
        print("Error: Both username and password are required.")
    if args.db:
        DB_PATH = args.db
    create_admin(args.username, args.password, DB_PATH)
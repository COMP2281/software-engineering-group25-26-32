import argparse, sqlite3, os, bcrypt
from dotenv import load_dotenv
load_dotenv()
try:
    DB_PATH = os.environ.get("DB_PATH")
except:
    DB_PATH = "./db/db.db"
if DB_PATH is None:
    DB_PATH = "./db/db.db"

def create_admin(username, password):
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
    except sqlite3.IntegrityError:
        print(f"Error: Admin user '{username}' already exists.")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Usage: python create-admin.py <username> <password>
    parser = argparse.ArgumentParser(description="Create an admin user for the thesis search application.")
    parser.add_argument("username", type=str, help="The username for the admin user.")
    parser.add_argument("password", type=str, help="The password for the admin user.")
    args = parser.parse_args()
    if not args.username or not args.password:
        print("Error: Both username and password are required.")
    create_admin(args.username, args.password)
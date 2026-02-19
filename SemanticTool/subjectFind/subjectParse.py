# Subjects actually don't exist in the db, use department instead?

import sqlite3

def get_unique_departments(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT department
        FROM Thesis
        WHERE department IS NOT NULL
          AND TRIM(department) != ''
        ORDER BY department;
    """)

    departments = [row[0].strip() for row in cursor.fetchall()]

    conn.close()
    return departments


def list_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table';
    """)

    tables = cursor.fetchall()
    conn.close()

    return [t[0] for t in tables]


if __name__ == "__main__":
    tables = list_tables("durhamDB.db")
    print("Tables found:")
    for t in tables:
        print("-", t)


departments = get_unique_departments("durhamDB.db")

print(f"Total departments: {len(departments)}")
for d in departments:
    print(d)



import sqlite3, json, os
from dotenv import load_dotenv
import google.genai as gemini
load_dotenv()
try:
    DB_PATH = os.environ.get("DB_PATH")
except:
    DB_PATH = "./db/db.db"
DOC_ID = 160


# load thesis pages from db
def load_pages(doc_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pdf_text
        FROM Thesis
        WHERE id = ?
    """, (doc_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return []

    raw_text = row[0]
    pages = []

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            pages.append(f"PAGE-{data['metadata']['page']}: \n {data['text']}")
        except:
            print("JSON parse error")
            continue
    pages = "\n".join(pages)
    return pages

# Summarise using Gemini - need GEMINI_API_KEY in .env
def summarise_thesis(DOC_ID=DOC_ID):
    pages = load_pages(DOC_ID)
    client = gemini.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=f"""
Summarise the following thesis text including:

- Overall theme
- Core research question or purpose
- Key arguments
- Important findings
- Methodology (if present)
- Conclusions
- Implications

Be detailed but concise Include page numbers of information used to generate the summary.
\n\n{pages}
""")
    res = response.text
    return res
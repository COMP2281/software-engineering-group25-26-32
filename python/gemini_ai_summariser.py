import sqlite3, json, os
from dotenv import load_dotenv
import google.genai as gemini
load_dotenv()
try:
    DB_PATH = os.environ.get("DB_PATH")
except:
    DB_PATH = "./db/db.db"
if DB_PATH is None:
    DB_PATH = "./db/db.db"
DOC_ID = 160
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
except:
    raise Exception("GEMINI_API_KEY environment variable not found. Please set it in .env")

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
            pages.append(f"PDF PAGE {data['metadata']['page']}: \n {data['text']}")
        except:
            print("JSON parse error")
            continue
    pages = "\n".join(pages)
    return pages

# Summarise using Gemini - need GEMINI_API_KEY in .env
def summarise_thesis(DOC_ID=DOC_ID):
    pages = load_pages(DOC_ID)
    try:
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

    Be detailed but concise. Include page numbers of information used to generate the summary.
    Produce your summary in a HTML format, using only <h5> and <h6> for headings and subheadings. 
    DO NOT WRAP THE SUMMARY IN ANY <html>, <code> etc TAGS,MARKDOWN CODE BLOCKS OR ANY OTHER CONTAINER
    \n\n{pages}
    """)
    except Exception as e:
        print("Error generating summary:", str(e))
        return "Error generating summary"
    res = response.text
    # seriously, gemini, at least be consistent with your formatting :/
    if res.find("```html") != -1:
        res = res.split("```html")[1].split("```")[0].strip()
    if res.find("<html>") != -1:
        res = res.split("<html>")[1].split("</html>")[0].strip()
    if res.find("<code>") != -1:
        res = res.split("<code>")[1].split("</code>")[0].strip()
        if res[0] == '"' and res[-1] == '"':
            res = res[1:-1]
    return res
from html.parser import HTMLParser
import os, sqlite3, time
import urllib.request
from dotenv import load_dotenv

load_dotenv()

RATE_LIMIT_PAUSE = 0.1

DB_PATH = os.environ.get("DB_PATH", "./db/db.db")
if not os.path.exists(DB_PATH):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.execute(
    '''
    CREATE TABLE IF NOT EXISTS "Thesis" (
    "id"	INTEGER NOT NULL,
    "title"	TEXT,
    "author"	TEXT,
    "abstract"	TEXT,
    "award"	NUMERIC,
    "keywords"	TEXT,
    "date"	NUMERIC,
    "faculty"	TEXT,
    "department"	TEXT,
    "url"	TEXT,
    "pdf_url"	TEXT,
    "pdf_text"	TEXT,
    PRIMARY KEY("id" AUTOINCREMENT)
    )
    '''
    )
conn.commit()
conn.close()

def get_table_data(mystr):
    tblStart = '<table style="margin-bottom: 1em" cellpadding="3" class="ep_block" border="0">'
    idx = mystr.find(tblStart)
    if idx != -1:
        idx2 = mystr.find("</table>", idx)
        table = mystr[idx:idx2]
        awardIdx = table.find('<th valign="top" class="ep_row">Award:</th>')
        if awardIdx != -1:
            awardEndIdx = table.find("</td>", awardIdx)
            award = table[awardIdx:awardEndIdx]
            award = award[award.find('<td valign="top" class="ep_row">')+len('<td valign="top" class="ep_row">'):]
        else:
            award = None
        deptIdx = table.find('<th valign="top" class="ep_row">Faculty and Department:</th>')
        if deptIdx != -1:
            deptEndIdx = table.find("</td>", deptIdx)
            dept = table[deptIdx:deptEndIdx]
            dept = dept[dept.find('<a'):]
            dept = dept[dept.find('">')+2:]
            dept = dept[:dept.find("</a>")]
            dept = dept.replace("&gt;", ";")
            try:
                faculty, dept = dept.split(";")
                faculty = faculty.split(" ", maxsplit=2)[-1].rstrip()
                dept = ",".join(dept.split(",")[:-1]).lstrip().rstrip()
            except:
                faculty = dept
                dept = None
        else:
            faculty = None
            dept = None
        return award, faculty, dept
    else:
        return None, None, None

def get_metadata(mystr):
    class MyHTMLParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.data = {
                "title": None,
                "author": None,
                "abstract": None,
                "award": None,
                "keywords":[],
                "date": None,
                "faculty": None,
                "department": None,
                "pdf_url": None,
            }
            self.public = True
            self.flag = False
        def handle_starttag(self, tag, attrs):
            if tag == "meta":
                # print("Encountered a meta tag :", tag)
                attributes = dict(attrs)
                if attributes.get("name") == "eprints.full_text_status":
                    self.public = (attributes.get("content") == "public")
                
                if attributes.get("name") == "eprints.title":
                    self.data["title"] = attributes.get("content")
                elif attributes.get("name") == "eprints.abstract":
                    self.data["abstract"] = attributes.get("content")
                elif attributes.get("name") == "eprints.date":
                    self.data["date"] = attributes.get("content")
                elif attributes.get("name") == "DC.creator":
                    self.data["author"] = attributes.get("content")
                elif attributes.get("name") == "DC.subject":
                    self.data["keywords"].append(attributes.get("content").lstrip().rstrip())
                elif attributes.get("name") == "eprints.document_url" and self.public:
                    self.data["pdf_url"] = attributes.get("content")

    parser = MyHTMLParser()
    parser.feed(mystr)
    parser.data["keywords"] = ", ".join(parser.data["keywords"])
    parser.data["award"], parser.data["faculty"], parser.data["department"] = get_table_data(mystr)
    return parser.data["title"], parser.data["author"], parser.data["abstract"], parser.data["award"], parser.data["keywords"], parser.data["date"], parser.data["faculty"], parser.data["department"], parser.data["pdf_url"]


def url_to_str(url):
    try:
        fp = urllib.request.urlopen(url)
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        return mystr
    except:
        return None

def write_to_db(title, author, abstract, award, keywords, date, faculty, dept, url, pdf_url, DB_PATH=DB_PATH):
    if title is None and author is None and abstract is None and award is None and keywords is None and date is None and faculty is None and dept is None and pdf_url is None:
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (title, author, abstract, award, keywords, date, faculty, dept, url, pdf_url)
    cur.execute("INSERT INTO Thesis (title, author, abstract, award, keywords, date, faculty, department, url, pdf_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    return

def scrape(i, DB_PATH=DB_PATH):
    url = f"https://etheses.dur.ac.uk/{i}/"
    mystr = url_to_str(url)
    if mystr is None:
        print("doesnt exist")
        return 1
    if '<p>You seem to be attempting to access an item that has been removed from the repository.</p>' in mystr:
        print("doesnt exist")
        return 1
    title, author, abstract, award, keywords, date, faculty, dept, pdf_url = get_metadata(mystr)
    write_to_db(title, author, abstract, award, keywords, date, faculty, dept, url, pdf_url, DB_PATH=DB_PATH)
    print("success", i)
    return 0

def get_last_id(DB_PATH=DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT url FROM Thesis WHERE url LIKE 'https://etheses.dur.ac.uk/%' ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        if row[0].find("https://etheses.dur.ac.uk/") == -1:
            return -1
        if row[0][-1] == "/":
            url = row[0][:-1]
        id = url.split("/")[-1]
        return int(id)
    else:
        return 0

def get_latest_id():
    mystr = url_to_str("https://etheses.dur.ac.uk/cgi/latest")
    if mystr is None:
        return None
    idx1 = mystr.find('<div class="ep_latest_result">')
    if idx1 != -1:
        mystr = mystr[idx1:]
        idx2 = mystr.find("</div>")
        latest_result = mystr[:idx2]
        a_start = latest_result.find('<a href="')
        a = latest_result[a_start+len('<a href="'):]
        if a_start != -1:
            a_end = a.find('/"')
            latest_id = (a[:a_end]).split("/")[-1]
            return int(latest_id)
    return None


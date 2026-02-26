import os, sqlite3, time
import urllib.request
from dotenv import load_dotenv

load_dotenv()

RATE_LIMIT_PAUSE = 0.1

try:
    DB_PATH = os.environ.get("DB_PATH")
except:
    DB_PATH = "./db/db.db"
if DB_PATH is None:
    DB_PATH = "./db/db.db"
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

def get_title(mystr):
    titleStr = "<h1"
    idx = mystr.find(titleStr)
    if idx != -1:
        idx = mystr.find(">", idx)
        idx2 = mystr.find("</h1>", idx)
        title = mystr[idx+1:idx2].lstrip().rstrip()
        title = title.replace("<br />", " ")
        title = title.replace("&amp;", "&")
    else:
        title = None
    return title

def get_author(mystr):
    authorStr = '<span class="person_name">'
    idx = mystr.find(authorStr)
    if idx != -1:
        idx2 = mystr.find("</span>", idx)
        author = mystr[idx+len(authorStr):idx2]
    else:
        author = None
    return author

def get_pdf_url(mystr):
    docUrlStr = '<span class="ep_document_citation">'
    idx = mystr.find(docUrlStr)
    if idx != -1:
        idx = mystr.find('href="', idx)
        idx += len('href="')
        idx2 = mystr.find('"', idx)
        pdf_url = mystr[idx:idx2]
        check = pdf_url.find("pdf")
        if check == -1:
            pdf_url = None
    else:
        pdf_url = None
    return pdf_url


def get_abstract(mystr):
    absStr = "<h2>Abstract</h2>"
    idx = mystr.find(absStr)
    if idx != -1:
        idx2 = mystr.find("</p>",idx)
        idx += len(absStr)
        abstract = mystr[idx:idx2]
        abstract = abstract.replace("<br />", "\n")
        abstract = abstract.replace("&#13;", "")
        endtag = abstract.find(">")
        abstract = abstract[endtag+1:]
    else:
        abstract = None
    return abstract



def get_data(mystr):
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
        keywordsIdx = table.find('<th valign="top" class="ep_row">Keywords:</th>')
        if keywordsIdx != -1:
            keywords = "Not available"
            keywordsEndIdx = table.find("</td>", keywordsIdx)
            keywords = table[keywordsIdx:keywordsEndIdx]
            keywords = keywords[keywords.find('<td valign="top" class="ep_row">')+len('<td valign="top" class="ep_row">'):]
            keywords = keywords.replace(";", ",")
        else:
            keywords = None
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
                faculty = faculty.split(" ", maxsplit=2)[-1]
                dept = ",".join(dept.split(",")[:-1]).lstrip()
            except:
                faculty = dept
                dept = None
        else:
            faculty = None
            dept = None
        dateIdx = table.find('<th valign="top" class="ep_row">Thesis Date:</th>')
        if dateIdx != -1:
            dateEndIdx = table.find("</td>", dateIdx)
            date = table[dateIdx:dateEndIdx]
            date = date[date.find('<td valign="top" class="ep_row">')+len('<td valign="top" class="ep_row">'):]
        else:
            date = None
        return award, keywords, date, faculty, dept
    else:
        return None, None, None, None, None

def write_to_db(title, author, abstract, award, keywords, date, faculty, dept, url, pdf_url, DB_PATH=DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (title, author, abstract, award, keywords, date, faculty, dept, url, pdf_url)
    cur.execute("INSERT INTO Thesis (title, author, abstract, award, keywords, date, faculty, department, url, pdf_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    return



def scrape(i, DB_PATH=DB_PATH):
    url = f"https://etheses.dur.ac.uk/{i}/"
    try:
        fp = urllib.request.urlopen(f"https://etheses.dur.ac.uk/{i}/")
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
    except:
        print("doesnt exist")
        return 1
    if '<p>You seem to be attempting to access an item that has been removed from the repository.</p>' in mystr:
        print("doesnt exist")
        return 1
    title = get_title(mystr)
    author = get_author(mystr)
    abstract = get_abstract(mystr)
    award, keywords, date, faculty, dept = get_data(mystr)
    pdf_url = get_pdf_url(mystr)
    write_to_db(title, author, abstract, award, keywords, date, faculty, dept, url, pdf_url)
    print("success", i)
    return 0

def get_last_id(DB_PATH=DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT url FROM Thesis WHERE url IS NOT NULL ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        if row[0].find("https://etheses.dur.ac.uk/") == -1:
            return -1
        url = row[0][:-1]
        id = url.split("/")[-1]
        return int(id)
    else:
        return 0

def get_latest_id(DB_PATH=DB_PATH):
    latest_page = urllib.request.urlopen("https://etheses.dur.ac.uk/cgi/latest")
    mybytes = latest_page.read()
    mystr = mybytes.decode("utf8")
    latest_page.close()
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


if __name__ == "__main__":
    print(get_last_id())
    print(get_latest_id())
    # start = 1
    # #url format: "https://etheses.dur.ac.uk/NUMBER/"
    # #check all NUMBERs in the for loop
    # for j in range(start,16398):
    #     with open("./python/progress.txt", "w") as f:
    #         f.write(str(j))
    #     scrape(j)
    #     time.sleep(RATE_LIMIT_PAUSE) 
RATE_LIMIT_PAUSE = 0.1
DB_PATH = "./db/db.db"

import urllib.request
import sqlite3
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



def get_pdf_url(mystr):
    docUrlStr = '<span class="ep_document_citation">'
    idx = mystr.find(docUrlStr)
    if idx != -1:
        idx = mystr.find('href="', idx)
        idx += len('href="')
        idx2 = mystr.find('"', idx)
        pdf_url = mystr[idx:idx2]
    else:
        pdf_url = None
    return pdf_url

import time

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
            faculty, dept = dept.split(";")
            faculty = faculty.split(" ", maxsplit=2)[-1]
            dept = ",".join(dept.split(",")[:-1]).lstrip()
        else:
            faculty = None
            dept = None
        dateIdx = table.find('<th valign="top" class="ep_row">Thesis Date:</th>')
        if dateIdx == -1:
            dateEndIdx = table.find("</td>", dateIdx)
            date = table[dateIdx:dateEndIdx]
            date = date[date.find('<td valign="top" class="ep_row">')+len('<td valign="top" class="ep_row">'):]
        else:
            date = None
        return award, keywords, date, faculty, dept
    else:
        return None, None, None, None, None

def write_to_db(title, abstract, award, keywords, date, faculty, dept, url, pdf_url):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = (title, abstract, award, keywords, date, faculty, dept, url, pdf_url)
    cur.execute("INSERT INTO Thesis (title, abstract, award, keywords, date, faculty, department, url, pdf_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    return



def scrape(i):
    try:
        url = f"https://etheses.dur.ac.uk/{i}/"
        try:
            fp = urllib.request.urlopen(f"https://etheses.dur.ac.uk/{i}/")
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            fp.close()
        except:
            print("doesnt exist")
            return
        if '<p>You seem to be attempting to access an item that has been removed from the repository.</p>' in mystr:
            print("doesnt exist")
            return
        title = get_title(mystr)
        abstract = get_abstract(mystr)
        print("")
        award, keywords, date, faculty, dept = get_data(mystr)
        pdf_url = get_pdf_url(mystr)
        write_to_db(title,abstract, award, keywords, date, faculty, dept, url, pdf_url)
    except:
        print("Error")

start = 1
with open("progress.txt", "r") as f: 
    start = int(f.readline())
#url format: "https://etheses.dur.ac.uk/NUMBER/"
#check all NUMBERs in the for loop
for j in range(start,16398):
    with open("progress.txt", "w") as f:
        f.write(str(j))
    scrape(j)
    time.sleep(RATE_LIMIT_PAUSE) 
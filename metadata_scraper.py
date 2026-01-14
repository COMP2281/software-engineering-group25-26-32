import urllib.request

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
        print(abstract)
    else:
        print("Abstract not avaliable")

def get_data(mystr):
    tblStart = '<table style="margin-bottom: 1em" cellpadding="3" class="ep_block" border="0">'
    idx = mystr.find(tblStart)
    if idx != -1:
        idx2 = mystr.find("</table>", idx)
        table = mystr[idx:idx2]
        awardIdx = table.find('<th valign="top" class="ep_row">Award:</th>')
        awardEndIdx = table.find("</td>", awardIdx)
        award = table[awardIdx:awardEndIdx]
        award = award[award.find('<td valign="top" class="ep_row">')+len('<td valign="top" class="ep_row">'):]
        keywordsIdx = table.find('<th valign="top" class="ep_row">Keywords:</th>')
        if keywordsIdx != -1:
            keywords = "Not available"
            keywordsEndIdx = table.find("</td>", keywordsIdx)
            keywords = table[keywordsIdx:keywordsEndIdx]
            keywords = keywords[keywords.find('<td valign="top" class="ep_row">')+len('<td valign="top" class="ep_row">'):]
        else:
            keywords = None
        deptInx = table.find('<th valign="top" class="ep_row">Faculty and Department:</th>')
        deptEndIdx = table.find("</td>", deptInx)
        dept = table[deptInx:deptEndIdx]
        dept = dept[dept.find('<a'):]
        dept = dept[dept.find('">')+2:]
        dept = dept[:dept.find("</a>")]
        dept = dept.replace("&gt;", ";")
        dateIdx = table.find('<th valign="top" class="ep_row">Thesis Date:</th>')
        dateEndIdx = table.find("</td>", dateIdx)
        date = table[dateIdx:dateEndIdx]
        date = date[date.find('<td valign="top" class="ep_row">')+len('<td valign="top" class="ep_row">'):]
        print("Date:", date)
        print("Keywords:", keywords)
        print("Department:", dept)
        print("Award:", award)
        #table = f"Award: {award}"
        #print(table)

def scrape(i):
    try:
        fp = urllib.request.urlopen(f"https://etheses.dur.ac.uk/{i}/")
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        get_abstract(mystr)
        print("")
        get_data(mystr)

    except:
        print("doesnt exist")


scrape(1)
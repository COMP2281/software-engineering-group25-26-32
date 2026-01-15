import pymupdf, requests, sqlite3, pymupdf.layout #do not remove pymupdf.layout it is used internally by pymupdf4llm.
import pymupdf4llm


def pdf_urls_from_id_list(l):
    DB_PATH = "./python/db/db.db"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT pdf_url FROM Thesis WHERE id IN ({",".join("?"*len(l))})", tuple(l))
    rows = cur.fetchall()
    conn.close()
    return rows

def pdf_to_txt(l, out="output.txt"):
    """Convert the contents of PDF files corresponding to the list of IDs l into a single TXT file
    \nl = list of IDs from the database
    \nout = output filename (default: output.txt)"""
    if type(l) is not list:
        l = [l]
    OUT_PATH = "./python/out/"
    rows = pdf_urls_from_id_list(l)
    out = open(f"{OUT_PATH}/{out}", "wb") 
    for row in rows:
        pdf_url = row[0]
        if pdf_url is not None:
            out.write(bytes(f"--- Start of document from {pdf_url} ---\n", "utf-8"))
            r = requests.get(pdf_url)
            data = r.content
            doc = pymupdf.Document(stream=data, filetype="pdf")
            for page in doc: # iterate the document pages
                text = page.get_text().encode("utf-8") 
                out.write(text)
                out.write(bytes((12,)))
            out.write(bytes(f"--- End of document from {pdf_url} ---\n\n", "utf-8"))
    doc.close()
    out.close()
    return

def pdf_to_md(l, out="output.md"):
    """Convert the contents of PDF files corresponding to the list of IDs l into a single MD file
    \nl = list of IDs from the database
    \nout = output filename (default: output.md)"""
    if type(l) is not list:
        l = [l]
    OUT_PATH = "./python/out/"
    rows = pdf_urls_from_id_list(l)
    out = open(f"{OUT_PATH}/{out}", "wb") 
    for row in rows:
        pdf_url = row[0]
        if pdf_url is not None:
            out.write(bytes(f"--- Start of document from {pdf_url} ---\n", "utf-8"))
            r = requests.get(pdf_url)
            data = r.content
            doc = pymupdf.Document(stream=data, filetype="pdf")
            md_text = pymupdf4llm.to_markdown(doc)
            out.write(md_text.encode("utf-8"))
            out.write(bytes(f"--- End of document from {pdf_url} ---\n\n", "utf-8"))
    doc.close()
    out.close()
    return

# convert PDF files to TXT or MD to be more LLM-friendly
# Note: MD is very slow compared to TXT but encodes extra structural information from the PDF.

#example usage:
pdf_to_txt([146])
pdf_to_md([146])
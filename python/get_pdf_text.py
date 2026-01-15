import pymupdf, requests, sqlite3, pymupdf.layout #do not remove pymupdf.layout it is used internally by pymupdf4llm.
import pymupdf4llm
from llama_index.core import Document


def pdf_urls_from_id_list(l):
    DB_PATH = "./python/db/db.db"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT pdf_url FROM Thesis WHERE id IN ({",".join("?"*len(l))})", tuple(l))
    rows = cur.fetchall()
    conn.close()
    return rows

def pdf_to_txt(l):
    """Convert the contents of PDF files corresponding to the input ID(s) into a single TXT file
    \nl = ID or list of IDs from the database
    """
    if type(l) is not list:
        l = [l]
    rows = pdf_urls_from_id_list(l)
    fulltext = "" 
    for row in rows:
        pdf_url = row[0]
        if pdf_url is not None:
            r = requests.get(pdf_url)
            data = r.content
            doc = pymupdf.Document(stream=data, filetype="pdf")
            for page in doc: # iterate the document pages
                text = page.get_text()
                fulltext += text + "\n"
            doc.close()
    return fulltext

def pdf_to_md(l):
    """Convert the contents of PDF files corresponding to the imput ID(s) into a single MD file
    \nl = ID or list of IDs from the database
    """
    if type(l) is not list:
        l = [l]
    rows = pdf_urls_from_id_list(l)
    for row in rows:
        pdf_url = row[0]
        if pdf_url is not None:
            r = requests.get(pdf_url)
            data = r.content
            doc = pymupdf.Document(stream=data, filetype="pdf")
            md_text = pymupdf4llm.to_markdown(doc)
            doc.close()
    return md_text

def pdf_to_llamadoc(l, how="txt"):
    """Convert the contents of PDF file(s) corresponding to the input ID(s) into a Llama Index Document list
    \nl = ID or list of IDs from the database
    \nhow = "txt" or "md" for text or markdown output (default: "txt"). Txt is significantly faster
    \nReturns a list of Llama Index Documents, one per page of each PDF."""
    if type(l) is not list:
        l = [l]
    rows = pdf_urls_from_id_list(l)
    llama_docs = []
    for row in rows:
        pdf_url = row[0]
        if pdf_url is not None:
            r = requests.get(pdf_url)
            data = r.content
            doc = pymupdf.Document(stream=data, filetype="pdf")
            if how == "md":
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    md_page = pymupdf4llm.to_markdown(page)
                    llama_docs.append(
                        Document(
                            text=md_page,
                            metadata={
                                "source": pdf_url,
                                "page": page_num + 1
                            }
                        )
                    )
            else:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_page = page.get_text()
                    llama_docs.append(
                        Document(
                            text=text_page,
                            metadata={
                                "source": pdf_url,
                                "page": page_num + 1
                            }
                        )
                    )
            doc.close()
    return llama_docs

def write_to_file(content, out="output.txt"):
    """Write content to a file in the out/ directory
    \ncontent = string content to write
    \nout = output filename (default: output.txt)"""
    OUT_PATH = "./python/out/"
    with open(f"{OUT_PATH}/{out}", "wb") as out_file:
        out_file.write(content.encode("utf-8"))
    return

# convert PDF files to TXT, MD or llamadocs to be more LLM-friendly
# Note: MD is very slow compared to TXT but encodes extra structural information from the PDF.

"""
Example usage:
    a = pdf_to_txt([147,146])
    b = pdf_to_md(146)
    c = pdf_to_llamadoc([146],how="txt")
    write_to_file(a, out="example_output.txt")
    write_to_file(b, out="example_output.md")
    <do llama shit with the llamadocs idk>

Notes:
- it takes ~2 seconds to convert to txt and ~61 seconds to convert to md, for a 281 page pdf.
- Some non-standard characters get borked in both txt and md outputs.
- Does not use OCR (as OCR is 1000 times slower). Only works for PDFs with embedded, non-obfuscated text.
"""
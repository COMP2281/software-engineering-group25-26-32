import os, json, pymupdf, requests, sqlite3, pymupdf.layout #do not remove pymupdf.layout it is used internally by pymupdf4llm.
import pymupdf4llm
from llama_index.core import Document
from dotenv import load_dotenv

load_dotenv()

def is_garbage(text):
    #very basic algorithm to determine if a page contains actual text or is binary garbage (i.e. detects if OCR is needed)
    return (sum(c.isalpha() for c in text) / max(len(text), 1) < 0.5) and (text.count(".")< 0.4*max(1,len(text))) and (text.count("-")< 0.4*max(1,len(text)))

def pdf_urls_from_id_list(l):
    DB_PATH = "./python/db/db.db"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT pdf_url FROM Thesis WHERE id IN ({",".join("?"*len(l))})", tuple(l))
    rows = cur.fetchall()
    conn.close()
    return rows

def page_ocr_text(page:pymupdf.Page):
    tessdata_dir = os.getenv("TESSDATA_PREFIX")
    print(tessdata_dir)
    if tessdata_dir is None:
        raise ValueError("TESSDATA_PREFIX environment variable not set. OCR cannot proceed.")
    tp = page.get_textpage_ocr(flags=0, dpi=300, full=True, tessdata=tessdata_dir)
    text = tp.extractText()
    return text


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
                if is_garbage(text):
                    text = page_ocr_text(page)
                fulltext += text + "\n"
            doc.close()
    return fulltext

def pdf_to_txt_json(l):
    """Convert the contents of PDF files corresponding to the input ID(s) into a JSON file. One line in the JSON file = one page in the pdf.
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
                if is_garbage(text):
                    text = page_ocr_text(page)
                json_ = {
                    "id" : pdf_url+"_page_"+str(page.number),
                    "text" : text,
                    "metadata" : {
                        "source": pdf_url,
                        "page": page.number + 1,
                        "type": "pdf"
                    }
                }
                text = json.dumps(json_, ensure_ascii=False)
                fulltext += text + "\n"
            doc.close()
            fulltext += "\n\n"
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
                    if is_garbage(page.get_text()):
                        text_page = page_ocr_text(page)
                    else:
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
    if type(content) is list:
        content = "\n".join([str(c) for c in content])
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
- OCR only supported for txt (and llamadoc with how=txt). It is very slow and can produce some weird shit
For OCR to work, need to clone https://github.com/tesseract-ocr/tessdata and set TESSDATA_PREFIX = path_to_cloned_tessdata in .env file.
"""
a = pdf_to_txt_json(145)
write_to_file(a, out="example_output.json")
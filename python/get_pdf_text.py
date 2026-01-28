import os, time, json, pymupdf, requests, sqlite3, pymupdf.layout #do not remove pymupdf.layout it is used internally by pymupdf4llm.
import pymupdf4llm
from dotenv import load_dotenv

load_dotenv()

def get_all_ids():
    DB_PATH = "./python/db/db.db"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM Thesis") 
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

def pdf_urls_from_id_list(l):
    DB_PATH = "./python/db/db.db"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT id, title, date, pdf_url FROM Thesis WHERE id IN ({",".join("?"*len(l))})", tuple(l))
    rows = cur.fetchall()
    conn.close()
    return rows

def is_garbage(text):
    #very basic algorithm to determine if a page contains actual text or is binary garbage (i.e. detects if OCR is needed)
    return (sum(c.isalpha() for c in text) / max(len(text), 1) < 0.5) and (text.count(".")< 0.4*max(1,len(text))) and (text.count("-")< 0.4*max(1,len(text)))


def page_ocr_text(page:pymupdf.Page):
    tessdata_dir = os.getenv("TESSDATA_PREFIX")
    if tessdata_dir is None:
        raise ValueError("TESSDATA_PREFIX environment variable not set. OCR cannot proceed.")
    tp = page.get_textpage_ocr(flags=0, dpi=300, full=True, tessdata=tessdata_dir)
    text = tp.extractText()
    return text


# def pdf_to_txt(id):
#     """Convert the contents of PDF files corresponding to the input ID(s) into a single TXT file
#     \nid = ID from the database
#     """
#     if type(id) is not list:
#         id = [id]
#     rows = pdf_urls_from_id_list(id)
#     fulltext = "" 
#     for row in rows:
#         pdf_url = row[3]
#         if pdf_url is not None:
#             r = requests.get(pdf_url)
#             data = r.content
#             doc = pymupdf.Document(stream=data, filetype="pdf")
#             for page in doc: # iterate the document pages
#                 text = page.get_text()
#                 if is_garbage(text):
#                     text = page_ocr_text(page)
#                 fulltext += text + "\n"
#             doc.close()
#     return fulltext

def pdf_to_txt_json(id):
    """Convert the contents of PDF files corresponding to the input ID into a JSON file. One line in the JSON file = one page in the pdf.
    \nid = ID from the database
    """
    if type(id) is not list:
        id = [id]
    rows = pdf_urls_from_id_list(id)
    fulltext = "" 
    for row in rows:
        id = row[0]
        title = row[1]
        date = row[2]
        pdf_url = row[3]
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

# def pdf_to_md(id):
#     """Convert the contents of PDF files corresponding to the imput ID(s) into a single MD file
#     \nid = ID from the database
#     """
#     if type(id) is not list:
#         id = [id]
#     rows = pdf_urls_from_id_list(id)
#     for row in rows:
#         pdf_url = row[3]
#         if pdf_url is not None:
#             r = requests.get(pdf_url)
#             data = r.content
#             doc = pymupdf.Document(stream=data, filetype="pdf")
#             md_text = pymupdf4llm.to_markdown(doc)
#             doc.close()
#     return md_text

# def pdf_to_llamadoc(id, how="txt"):
#     """Convert the contents of PDF file(s) corresponding to the input ID(s) into a Llama Index Document list
#     \nid = ID from the database
#     \nhow = "txt" or "md" for text or markdown output (default: "txt"). Txt is significantly faster
#     \nReturns a list of Llama Index Documents, one per page of each PDF."""
#     if type(id) is not list:
#         id = [id]
#     rows = pdf_urls_from_id_list(id)
#     llama_docs = []
#     for row in rows:
#         pdf_url = row[3]
#         if pdf_url is not None:
#             r = requests.get(pdf_url)
#             data = r.content
#             doc = pymupdf.Document(stream=data, filetype="pdf")
#             if how == "md":
#                 for page_num in range(len(doc)):
#                     page = doc.load_page(page_num)
#                     md_page = pymupdf4llm.to_markdown(page)
#                     llama_docs.append(
#                         Document(
#                             text=md_page,
#                             metadata={
#                                 "source": pdf_url,
#                                 "page": page_num + 1
#                             }
#                         )
#                     )
#             else:
#                 for page_num in range(len(doc)):
#                     page = doc.load_page(page_num)
#                     if is_garbage(page.get_text()):
#                         text_page = page_ocr_text(page)
#                     else:
#                         text_page = page.get_text()
#                     llama_docs.append(
#                         Document(
#                             text=text_page,
#                             metadata={
#                                 "source": pdf_url,
#                                 "page": page_num + 1
#                             }
#                         )
#                     )
#             doc.close()
#     return llama_docs

# def write_to_file(content, out="output.txt"):
#     """Write content to a file in the out/ directory
#     \ncontent = string content to write
#     \nout = output filename (default: output.txt)"""
#     if type(content) is list:
#         content = "\n".join([str(c) for c in content])
#     OUT_PATH = "./python/out/"
#     with open(f"{OUT_PATH}/{out}", "wb") as out_file:
#         out_file.write(content.encode("utf-8"))
#     return

def doc_text_to_db(id, text):
    """Update the database entry for the given ID with the provided text
    \nid = ID from the database
    \ntext = text content to store in the database"""
    DB_PATH = "./python/db/db.db"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE Thesis SET pdf_text = ? WHERE id = ?", (text, id))
    conn.commit()
    conn.close()
    return

def upload_pdf_texts_to_db():
    """Convert **ALL** PDFs in the database to text and upload to the database"""
    all_ids = get_all_ids()
    all_ids = [id for id in all_ids if id >= 4382]
    ctr = 0
    for id in all_ids:
        if ctr % 10 == 0 and ctr > 0:
            print(f"Processed {ctr} PDFs...")
            time.sleep(10) #avoid overwhelming any servers
        print(f"Processing ID {id}...")
        try:
            text = pdf_to_txt_json(id)
            doc_text_to_db(id, text)
        except Exception as e:
            print(f"Error processing ID {id}: {e}")
        ctr +=1
    return

def get_pdf_text(id):
    """Retrieve the stored PDF text from the database for the given ID
    \nid = ID from the database
    \nReturns the stored PDF text as a string"""
    DB_PATH = "./python/db/db.db"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT pdf_text FROM Thesis WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
# convert PDF files to TXT, MD or llamadocs to be more LLM-friendly
# Note: MD is very slow compared to TXT but encodes extra structural information from the PDF.

"""
Example usage:
    id = 145
    j = pdf_to_txt_json(id)
    doc_text_to_db(id, j)

Notes:
- it takes ~2 seconds to convert to txt/json and ~61 seconds to convert to md (with formatting), for a 281 page pdf (no OCR).
- Some non-standard characters get borked in both txt and md outputs.
- OCR is supported for txt/json. It is very slow and can produce some weird shit, but is required for a significant number of the theses that either
  use a weird text encoding or are handwritten.
- OCR final boss is the shit from 1925, even I cant decipher that so OCR has no chance.
IMPORTANT: For OCR to work, need to clone https://github.com/tesseract-ocr/tessdata and set TESSDATA_PREFIX = path_to_cloned_tessdata in .env file.
"""
# doc_text_to_db(145, a)
# b = get_pdf_text(145)
# write_to_file(b, out="out.json")
upload_pdf_texts_to_db()
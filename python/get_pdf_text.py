import os, time, json, pymupdf, requests, sqlite3, multiprocessing, queue, threading
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()
RATE_LIMIT_PAUSE = 6.7
try:
    DB_PATH = os.environ.get("DB_PATH")
except:
    DB_PATH = "./db/db.db"
if DB_PATH is None:
    DB_PATH = "./db/db.db"
TESSDATA_PATH = os.getenv("TESSDATA_PREFIX")


def get_unprocessed_ids(DB_PATH=DB_PATH):
    """Get all IDs from the db that havent currently been processed"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, pdf_url FROM Thesis WHERE pdf_text IS NULL AND pdf_url IS NOT NULL") 
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows if row[1].find(".pdf") != -1]

def pdf_urls_from_id_list(l, DB_PATH=DB_PATH):
    """Get the PDF URLs corresponding to a list of IDs from the database"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT id, title, date, pdf_url FROM Thesis WHERE id IN ({','.join('?'*len(l))})", tuple(l))
    rows = cur.fetchall()
    conn.close()
    return rows

def is_garbage(text):
    """***very*** basic algorithm to determine if a page contains actual text or is binary garbage (i.e. detects if OCR is needed)"""
    return (sum(c.isalpha() for c in text) / max(len(text), 1) < 0.5) and (text.count(".")< 0.4*max(1,len(text))) and (text.count("-")< 0.4*max(1,len(text)))


def page_ocr_text(page:pymupdf.Page):
    """Perform OCR on a page. Note: requires tessdata to be installed from https://github.com/tesseract-ocr/tessdata and the TESSDATA_PREFIX environment variable to be set to the tessdata directory"""
    if TESSDATA_PATH is None:
        raise ValueError("TESSDATA_PREFIX environment variable not set. OCR cannot proceed.")
    tp = page.get_textpage_ocr(flags=0, dpi=300, full=True, tessdata=TESSDATA_PATH)
    text = tp.extractText()
    return text


def pdf_to_txt_json(id, DB_PATH=DB_PATH):
    """Convert the contents of PDF files corresponding to the input ID into a JSON file. One line in the JSON file = one page in the pdf.
    \nid = ID from the database
    """
    if type(id) is not list:
        id = [id]
    rows = pdf_urls_from_id_list(id, DB_PATH=DB_PATH)
    fulltext = "" 
    for row in rows:
        id = row[0]
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

def doc_text_to_db(id, text, DB_PATH=DB_PATH):
    """Update the database entry for the given ID with the provided text
    \nid = ID from the database
    \ntext = text content to store in the database"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE Thesis SET pdf_text = ? WHERE id = ?", (text, id))
    conn.commit()
    conn.close()
    return


def get_pdf_text(id, DB_PATH=DB_PATH):
    """Retrieve the stored PDF text from the database for the given ID
    \nid = ID from the database
    \nReturns the stored PDF text as a string"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT pdf_text FROM Thesis WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
    

def process_pdf(id, DB_PATH=DB_PATH):
    print(f"Processing ID {id}...")
    time.sleep(RATE_LIMIT_PAUSE) 
    try:
        text = pdf_to_txt_json(id, DB_PATH=DB_PATH)
        return (id, text, None)
    except Exception as e:
        return (id, None, str(e))


def writer_thread(result_queue, DB_PATH=DB_PATH):
    """Thread to write PDF contents to DB once they've been OCR'd"""
    while True:
        item = result_queue.get()
        if item is None:
            break
        id, text, error = item
        if error:
            print(f"Error processing ID {id}: {error}")
        else:
            doc_text_to_db(id, text, DB_PATH=DB_PATH)
            print(f"Finished processing ID {id}")


def upload_pdf_texts_to_db_parallel(DB_PATH=DB_PATH):
    ids = [id for id in get_unprocessed_ids(DB_PATH=DB_PATH)]
    print(ids)
    print(len(ids))
    result_queue = queue.Queue()

    # Start DB writer thread
    writer = threading.Thread(target=writer_thread, args=(result_queue, DB_PATH))
    writer.start()

    with concurrent.futures.ProcessPoolExecutor(
        max_workers=multiprocessing.cpu_count()
    ) as executor:

        futures = [executor.submit(process_pdf, id, DB_PATH=DB_PATH) for id in ids]

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result_queue.put(future.result())

            if i % 10 == 0 and i > 0:
                print(f"Processed {i} PDFs...")

    # Stop writer
    result_queue.put(None)
    writer.join()


if __name__ == "__main__":
    upload_pdf_texts_to_db_parallel()
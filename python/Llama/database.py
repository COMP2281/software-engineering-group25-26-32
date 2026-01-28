import sqlite3
import os
import json


def chunkGen(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    text = text.strip()

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Find next sentence
        if end < len(text):
            last_period = chunk.rfind(".")
            if last_period != -1 and last_period > chunk_size * 0.5:
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = max(end - overlap, 0)

    return chunks


def embedGen(): 
    pass


def storeGen():
    pass    


def safe_json_lines(text):
    buffer = ""
    line_num = 0
    for line in text.splitlines():
        line_num += 1
        stripped = line.strip()
        if not stripped:
            continue

        buffer += stripped
        try:
            obj = json.loads(buffer)
            yield obj, line_num
            buffer = ""
        except json.JSONDecodeError:
            buffer += " "  # keep accumulating

    # If buffer is non-empty after all lines, it's broken
    if buffer.strip():
        yield None, line_num  # mark broken last chunk


def proprocPDF(pdf_text):
    pages = []
    failed_lines = []

    for obj, line_num in safe_json_lines(pdf_text):
        if obj is not None:
            pages.append(obj)
        else:
            print(f"✗ JSON ERROR at or before line {line_num}")
            failed_lines.append(line_num)

    if not pages:
        return "", {"source": "unknown", "pages": 0}, failed_lines

    full_text = "\n\n".join(
        page["text"] for page in pages if page["text"].strip()
    )
    metadata = {
        "source": pages[0]["metadata"]["source"],
        "pages": len(pages)
    }
    print(metadata)
    # print(full_text)
    return full_text, metadata, failed_lines


dirname = os.path.dirname(__file__)
dbfile = os.path.join(dirname, "db.db")
conn = sqlite3.connect(dbfile)
cur = conn.cursor()

documents = []
for (pdf_text,) in cur.execute("SELECT pdf_text FROM Thesis"):
    full_text, meta, failed_lines = proprocPDF(pdf_text)

    if failed_lines:
        # Skip it if there are JSON errors
        pass

    chunks = chunkGen(full_text)

    for i, chunk in enumerate(chunks):
        documents.append({
            "id": f"{meta['source']}_chunk_{i}",
            "text": chunk,
            "metadata": {
                **meta,
                "chunk_id": i
            }
        })


import sqlite3, json, ollama
# Ollama Thesis Summariser - extremely slow given our hardware limitations
# (takes like 10 minutes to summarise a 150 page thesis with GPU) but the summary is kinda decent
# Requires isntallation of Ollama and Mistral model (ollama pull mistral)

DB_PATH = "./db/db.db"
DOC_ID = 160
MODEL = "mistral"
PAGES_PER_CHUNK = 3
CHUNK_SUMMARIES_PER_MERGE = 6

# load thesis pages from db
def load_pages(doc_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pdf_text
        FROM Thesis
        WHERE id = ?
    """, (doc_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return []

    raw_text = row[0]
    pages = []

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            pages.append(data["text"])
        except:
            print("JSON parse error")
            continue
    return pages




# Ollama summarisation
def summarise(text, instruction):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a precise academic summariser."},
            {"role": "user", "content": f"{instruction}\n\n{text}"}
        ],
        options={"temperature": 0.2}
    )

    return response["message"]["content"].strip()



def summarise_thesis(DOC_ID=DOC_ID):
    print("Loading pages...")
    pages = load_pages(DOC_ID)
    if pages == []:
        print("Error reading thesis from DB")
        return
    print(f"{len(pages)} pages loaded.\n")

    # Summarising chunks of pages
    # (pages per chunk is defined in the variable PAGES_PER_CHUNK)
    # Note: if this is too high it will be truncated due to model context limit
    print("Summarising page groups...")
    page_chunks = [pages[i:i+PAGES_PER_CHUNK] for i in range(0, len(pages), PAGES_PER_CHUNK)]

    chunk_summaries = []

    for i, chunk in enumerate(page_chunks):
        print(f"Chunk {i+1}/{len(page_chunks)}")

        combined_text = "\n\n".join(chunk)

        summary = summarise(
            combined_text,
            instruction="""
Summarise this section of a long academic document.
Preserve key arguments, definitions, and findings.
"""
        )

        chunk_summaries.append(summary)

    # Merging the chunk summaries together
    print("\nConsolidating section summaries...")

    merge_groups = [chunk_summaries[i:i+CHUNK_SUMMARIES_PER_MERGE] for i in range(0, len(chunk_summaries), CHUNK_SUMMARIES_PER_MERGE)]
    merged_summaries = []

    for i, group in enumerate(merge_groups):
        print(f"Merge group {i+1}/{len(merge_groups)}")

        combined = "\n\n".join(group)

        merged = summarise(
            combined,
            instruction="""
Combine these section summaries into a coherent higher-level summary.
Remove redundancy while preserving key insights.
"""
        )

        merged_summaries.append(merged)

    # Merging the merged summaries into an overall summary of the whole thesis
    print("Creating final structured summary...")

    combined_final = "\n\n".join(merged_summaries)

    final_summary = summarise(
        combined_final,
        instruction="""
Produce a structured final summary including:

- Overall theme
- Core research question or purpose
- Key arguments
- Important findings
- Methodology (if present)
- Conclusions
- Implications

Be detailed but concise.
"""
    )

    print("\nFINAL SUMMARY:\n")
    print(final_summary)
    return final_summary


if __name__ == "__main__":
    summarise_thesis()
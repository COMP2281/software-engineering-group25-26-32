# First-time Setup:

## Required Files
### Durham E-Theses Database:
https://a.piggypiggyyoinkyoink.website/dingus/db/db.db
Place in `python/db` folder

### durham_thesis.index:
https://a.piggypiggyyoinkyoink.website/dingus/db/durham_thesis.index
place in `python` folder (no sub-folders)
### durham_thesis_ids.npy:
https://a.piggypiggyyoinkyoink.website/dingus/db/durham_thesis_ids.npy
place in `python` folder (no sub-folders)


## Node.js:
- `cd nodejs`
- `npm install`


## Python
Using python version 3.11.x (**Important. Please use the same version to avoid conflicts with packages**):
- `cd python`
- `python -m venv .venv`
- MacOS: `source .venv/bin/activate`, Windows: `./.venv/Scripts/activate`
- `pip install -r requirements.txt`

## Environment Variables
Create a file in the `python` folder called `.env` and insert the following lines:
```
TESSDATA_PREFIX = <...>/tessdata  
DB_PATH = <...>/db.db  
GEMINI_API_KEY = <your_gemini_api_key>  
SECRET_KEY = <KEYHERE>
```
Replacing `<...>` with the correct paths to the files on your machine, and `<your_gemini_api_key>` with your Gemini API key  
Tessdata can be cloned from https://github.com/tesseract-ocr/tessdata and is required to add full thesis texts to the database.  
A Gemini API key can be generated from https://aistudio.google.com/api-keys
Default db path is ./db/db.db

Replace '<KEYHERE>' with your secret key

# Running the code:

## Node.js
- `cd nodejs`
- `npm start`
- go to http://localhost:8080/  

## Python FastAPI:
- `cd python`
- `fastapi dev main.py`
- wait for `Application Startup Complete` message in console.

# Creating an Admin User
- `cd python`
- `python create_admin.py <username> <password>`
- Login with the credentials at http://localhost:8080/login

# Running tests
API endpoint tests are in `test_main.py` These purely test the functionality of the API, while mocking external function calls and DB queries.   
Running tests:
- Ensure Python modules `pytest` and `httpx` are installed in the virtual environment (they are in `requirements.txt` now)

Windows Powershell:
- `./test`

Bash:
- `./test.sh`


# Maintenance
- Ensure DB generally up to date (can be put on a schedule to update or hooked to the Durham E-theses)
    - Anytime the DB is updated, the model needs to be reindexed via the admin page or manually via index.py
- Ensure the Gemini API Key has sufficient credits / sufficient access permissions

# TODO
- ~~Show similarity score~~
- ~~Copy files instead of just replacing them~~
    - Updates to add "NEW" to the filename (same file extension)
    - Button to upload/replace the old files with the new ones (Ask if they wish to download the old ones for redundancy)
~~- Multithreading/Multiprocessing where necessary (AI Summary, Searching, etc)~~
- Curl testing for API endpoints (goes hand in hand)
- ~~Generate citations (different standards)~~
- ~~Further search/prying through via user questions~~
- ~~Text is formatted from summaries~~
- Continue conversation for gemini?
- Return messages somehow gone ?

# TODO List 2 the sequel
~~- Deleting users in db~~
~~- Sign out users~~
- Admin page frontend?



# TODO Unit Testing
 - get_pdf_text.py
 - index.py
 - search.py
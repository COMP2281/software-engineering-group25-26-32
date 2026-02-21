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
```
Replacing `<...>` with the correct paths to the files on your machine, and `<your_gemini_api_key>` with your Gemini API key  
Tessdata can be cloned from https://github.com/tesseract-ocr/tessdata and is required to add full thesis texts to the database.  
A Gemini API key can be generated from https://aistudio.google.com/api-keys


# Running the code:

## Node.js
- `cd nodejs`
- `npm start`
- go to http://localhost:8080/  

## Python FastAPI:
- `cd python`
- `fastapi dev main.py`
- wait for `Application Startup Complete` message in console.

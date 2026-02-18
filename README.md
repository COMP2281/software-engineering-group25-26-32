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


# Running the code:

## Node.js
- `cd nodejs`
- `npm start`
- go to http://localhost:8080/  

## Python FastAPI:
- `cd python`
- `fastapi dev main.py`
- wait for `Application Startup Complete` message in console.

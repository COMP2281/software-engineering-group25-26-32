# First-time Setup:

## Required Files
- theses_utf8.csv: https://a.piggypiggyyoinkyoink.website/dingus/db/theses_utf8.csv
- thesis.index: https://a.piggypiggyyoinkyoink.website/dingus/db/thesis.index
- thesis_ids.npy: https://a.piggypiggyyoinkyoink.website/dingus/db/thesis_ids.npy
- Place all three files in the `python` folder (not in any sub-folders)

## Node.js:
- `cd nodejs`
- `npm install`


## Python
Using python version 3.11.x (**Important. Please use the same version to avoid conflicts with packages**):
- `cd python`
- `python -m venv .venv`
- `source .venv/bin/activate` (one Windows: `./.venv/Scripts/activate`) 
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

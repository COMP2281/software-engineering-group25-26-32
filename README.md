## Run Node.js:
- `cd nodejs`
- `npm start`
- go to http://localhost:8080/  

## Run FastAPI
Using python version 3.11.13 (!!!Important. Please use the same version to avoid conflicts with packages)
- `cd python`
- `python -m venv .venv` (if that doesnt work on Windows try `py` instead of `python`)
- `source .venv/bin/activate` (if that doesnt work on Windows try `./.venv/Scripts/activate`)
- `pip install -r requirements.txt`
- `fastapi dev main.py`
- fastAPI is now running at http://localhost:8000/ 

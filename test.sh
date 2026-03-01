export PYTHONPATH=.
cd python 
source .venv/bin/activate || source .venv/Scripts/activate
pytest --cov=.
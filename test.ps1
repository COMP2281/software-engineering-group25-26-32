$env:PYTHONPATH="."
cd python
./.venv/Scripts/activate
pytest --cov=.
cd ..
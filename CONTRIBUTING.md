# Contributing

## Workflow

1. Create a branch from `main`.
2. Make a focused change.
3. Run the local checks before opening a pull request.
4. Open a pull request and request review from at least one teammate.
5. Do not merge unless CI passes.

## Local checks

From the repository root:

```bash
cd python
pytest --cov=. --cov-report=term-missing
cd ../nodejs
npm audit
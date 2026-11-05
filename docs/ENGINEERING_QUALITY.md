# Engineering Quality Gate

This repository uses GitHub Actions to check the Python core before changes are merged.

## Automated checks

- Python 3.12 environment
- Syntax compilation for the BONGO package, tests, and NEXORA entry modules
- Full pytest suite
- NEXORA logical-agent registry invariants (1,000 unique definitions across 20 departments)

## What a green workflow means

A passing workflow means the checks above passed in GitHub's runner. It does **not** prove that external model providers, payment services, deployment targets, or every optional integration are configured or reachable.

## Local verification

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python -m compileall -q bongo tests
python -m py_compile server.py nexora_agents.py nexora_model_adapter.py
python -m pytest -q
```

## Change policy

- Preserve the existing BONGO and NEXORA project boundaries.
- Keep credentials in environment variables or a secret manager; never commit local `.env` files.
- Treat registry entries as logical agent definitions, not proof of running autonomous workers.
- Add integration tests before claiming external services are production-ready.

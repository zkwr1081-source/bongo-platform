# NEXORA model adapter setup

The repository contains 1,000 **logical** agent profiles. To give selected
agents model-backed responses, configure an OpenAI-compatible Chat Completions
provider and run the adapter. This does not mean 1,000 agents are continuously
running.

## 1. Configure credentials

Set these in your shell or a local, untracked `.env` file. Never commit API keys.

- `NEXORA_BASE_URL`: provider API base, for example `https://api.openai.com/v1`
- `NEXORA_API_KEY`: secret API key from your provider
- `NEXORA_MODEL`: model identifier enabled for that key

## 2. Run the two-agent smoke test

From the repository root:

```bash
export NEXORA_BASE_URL="https://api.openai.com/v1"
export NEXORA_API_KEY="YOUR_KEY"
export NEXORA_MODEL="YOUR_ENABLED_MODEL"
python nexora_model_adapter.py
```

The example deliberately selects two agents with concurrency set to two.
Provider pricing, quotas, and rate limits apply. Do not raise concurrency
until the small test succeeds and you have checked provider limits.

## 3. Run tests

```bash
python -m unittest discover -s tests -p 'test_nexora*.py'
```

## Implementation notes

- Uses Python standard-library HTTP and async thread offloading; no extra package
  is required for this adapter.
- Credentials are read from environment variables and are not printed.
- Provider errors and malformed responses are surfaced as per-agent failures
  by the bounded runner.
- Only the Chat Completions request shape is assumed. Confirm that your chosen
  provider supports `POST /chat/completions` at the configured base URL.

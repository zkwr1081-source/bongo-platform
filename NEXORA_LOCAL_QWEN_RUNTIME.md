# NEXORA local Qwen runtime

## Local Termux configuration

The model adapter supports an OpenAI-compatible local endpoint without an API key.
Keep the model server bound to loopback and configure the runtime in the same Termux
session that starts the NEXORA API:

```bash
export NEXORA_BASE_URL="http://127.0.0.1:8090/v1"
export NEXORA_MODEL="qwen2.5-3b"
export NEXORA_MODEL_TIMEOUT="300"
python server.py
```

For a remote provider, use HTTPS and set `NEXORA_API_KEY` in the process environment.
Never commit credentials or expose the local model/API port to an untrusted network.

## Execution limits

The logical registry contains 1,000 agent specifications; it does not create 1,000
independent model processes. The HTTP execution endpoint accepts at most 10 selected
agents per request. Start with one or two agents on a phone, then increase concurrency
only after observing latency, memory use, and provider limits.

## Verify

```bash
python -m unittest discover -s tests -p 'test_nexora*.py'
python nexora_model_adapter.py
```

The smoke command makes real provider requests to two selected agents. A successful
registry test alone is not evidence of model inference. The dashboard status must not
be interpreted as a live model health check unless a provider request has actually run.

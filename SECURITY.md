# Security Policy

## Supported deployment boundary

NEXORA's dashboard and agent execution server is intended for local-first operation.

- The default bind address is `127.0.0.1`.
- Unauthenticated agent execution is permitted only for loopback binds (`127.0.0.1`, `::1`, or `localhost`).
- A non-loopback bind is rejected at startup unless `NEXORA_EXECUTION_TOKEN` is configured.
- When the token is configured, every `POST /api/agents/run` request must include `Authorization: Bearer <token>`, including requests from localhost.
- Token comparison uses a constant-time comparison. The application does not write the token to its request logs.
- The browser dashboard provides a password field for the execution token. The value stays in page memory, is sent only as a same-origin Bearer header, and is not written to localStorage. Reloading the page clears the field.

## Safe local operation

Run with the default loopback bind:

```sh
python server.py
```

Keep the service on the same device. Do not forward port 8080 to an untrusted network.

## Network or reverse-proxy operation

Before using a non-loopback bind:

1. Store a high-entropy `NEXORA_EXECUTION_TOKEN` in the host's secret manager or protected process environment.
2. Use HTTPS at a trusted reverse proxy; do not expose the plain HTTP listener to the public Internet.
3. Restrict network ingress to trusted clients and configure request-rate and connection limits at the proxy.
4. Ensure clients send the Bearer token over TLS. Do not place it in URLs, browser local storage, source code, logs, or issue reports.
5. Rotate the token immediately if it may have been exposed.

Example client request (the token value stays in the process environment):

```sh
curl --fail-with-body \
  -H "Authorization: Bearer $NEXORA_EXECUTION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"goal":"Review the service health endpoint"}' \
  https://your-trusted-host.example/api/agents/run
```

The example is a request format only; it does not imply that a deployment exists.

## Data and execution boundaries

- Never commit `.env` files, provider keys, Telegram tokens, recovery codes, wallet secrets, or payment credentials.
- Model-provider configuration is separate from the execution token.
- The agent endpoint invokes the configured model handler; it does not grant arbitrary shell, wallet, exchange, or payment access.
- A successful HTTP response does not prove a task's business outcome or production deployment.
- Configure backups and retention for any persistent data before enabling production workloads.

## Reporting a vulnerability

Do not publish credentials or exploit details in public issues. Use GitHub's private vulnerability reporting feature for this repository when available, or contact the repository owner through a private channel. Include the affected commit, impact, and a minimal reproduction without real secrets or customer data.

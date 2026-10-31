# Private Telegram GitHub Newsletter Bot

Arabic-first private bot for hourly portfolio progress digests and on-demand reports.

## What it does

- Polls GitHub for commits in the last 24 hours, open pull requests, and recently updated open issues across configured repositories.
- Sends a private newsletter to allowlisted Telegram user IDs approximately once per hour while the process is running.
- Provides `/now`, `/projects`, and `/ideas` commands.
- Optionally uses the OpenAI Responses API to turn repository facts into an Arabic engineering summary. Without an OpenAI key, it sends a factual template.
- Rejects Telegram users not listed in `ALLOWED_TELEGRAM_USER_IDS`.

## Configure safely

1. Create a bot with Telegram's official `@BotFather` and copy its token directly into your hosting provider's secret manager. Never commit the token.
2. Obtain your numeric Telegram user ID from a trusted Telegram ID utility or your own trusted bot tooling, then set `ALLOWED_TELEGRAM_USER_IDS`. Do not publish it unnecessarily.
3. Configure `GITHUB_TOKEN` as a fine-grained token with read-only access to the selected repositories (Contents/Metadata/Pull requests/Issues as required). Public repository reads may work without it, but rate limits are lower.
4. Optionally set `OPENAI_API_KEY` in the host's secret manager. This is an API integration, not a direct connection to the ChatGPT conversation. API usage may incur charges.
5. Deploy this folder as a continuously running container on a host that supports persistent processes. Set the environment variables from `.env.example`; do not upload a real `.env` file.

## Local run

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill values locally; do not commit .env
set -a; . ./.env; set +a
python bot.py
```

## Limitations

- The hourly interval is approximate; host sleep, restarts, rate limits, or network failures can delay a report.
- The report describes GitHub activity; it cannot see work outside connected repositories or prove that a feature is deployed or earning revenue.
- It does not merge PRs, deploy software, or transfer money.
- This repository folder is implementation code, not a live bot. It becomes operational only after secure configuration and deployment.
- OpenAI API calls are separate from ChatGPT Plus/Free access and require an API key and separate billing.

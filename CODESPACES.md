# BONGO on GitHub Codespaces

This repository includes a cloud development environment. Codespaces provides a real Linux terminal and editor attached to this GitHub repository; it does not connect to or control the owner's Android/Termux filesystem.

## Start a Codespace

1. Open the repository on GitHub.
2. Select the branch `codex/codespaces-dev-environment`.
3. Open **Code → Codespaces → Create codespace on ...**.
4. Wait for the container setup to finish.
5. Open the integrated terminal and run:

   ```bash
   bash scripts/dev-check.sh
   ```

The environment installs the Python dependencies and GitHub CLI. Ports 8092 and 8093 are configured for forwarding when the corresponding services are started manually.

## Connect from Termux (optional)

Install GitHub CLI in Termux if it is not already installed, then authenticate through the browser:

```bash
gh auth login
gh codespace list
```

Copy the Codespace name shown by the list and connect:

```bash
gh codespace ssh -c YOUR_CODESPACE_NAME
```

Replace `YOUR_CODESPACE_NAME` with the actual name. Do not paste access tokens, passwords, SSH private keys, or recovery phrases into chat.

## Git workflow

Use a dedicated feature branch for changes. Review `git diff`, run the checks, then commit and push only the intended files. Open a Pull Request for review. Do not push directly to `main`.

## Safety boundaries

- No secrets, local databases, wallet files, or Termux home-directory contents are copied into this Codespace automatically.
- The CI workflow has read-only repository permissions and runs syntax checks and tests only.
- No deployment, production start, asset transfer, wallet signing, or automatic merge is configured.
- Codespaces usage may be subject to the account's included quota and billing settings.

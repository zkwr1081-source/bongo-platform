# Contributing to BONGO

Thank you for helping improve BONGO — the integrated solutions platform.

This guide describes a safe, reviewable contribution process. The goal is to improve reliability and maintainability **without changing the project's core purpose, service boundaries, or established behavior unintentionally**.

## Project principles

- Preserve BONGO's identity as a platform for discovering, integrating, operating, and monitoring services.
- Respect existing module boundaries and public API contracts.
- Prefer small, focused changes over broad rewrites.
- Keep integrations replaceable and testable.
- Never commit credentials, tokens, private keys, production data, or local `.env` files.
- Document behavior changes and compatibility implications.

## Before making a change

1. Read the relevant source files and existing documentation.
2. Identify the owning module and the interfaces it depends on.
3. Check related issues and open pull requests to avoid duplicate work.
4. Record the expected behavior and how it can be verified.
5. If a change could alter architecture, data formats, authentication, or public APIs, describe the impact before implementation.

## Development workflow

1. Create a focused branch from the current `main` branch.
2. Make the smallest coherent change that solves the problem.
3. Add or update tests for changed behavior where the project has a test structure.
4. Update documentation and configuration examples when behavior or setup changes.
5. Review the complete diff for accidental deletions, secrets, generated files, and unrelated formatting changes.
6. Open a pull request with a clear summary, rationale, verification notes, and known limitations.

## Validation

Use the commands and environment documented by the repository. At minimum:

- Verify Python syntax for changed Python modules.
- Run the project's existing automated test suite, if present.
- Run configured linting, type checks, and CI workflows, if present.
- Verify setup/configuration examples without exposing real credentials.

Do not report a check as passing unless it was actually run and its result was observed. If a check cannot be run, state why.

## Pull request checklist

- [ ] The change preserves BONGO's core purpose and existing architecture.
- [ ] The scope is focused and backward compatibility has been considered.
- [ ] Tests or a clear manual verification procedure are included.
- [ ] Documentation is updated where needed.
- [ ] No secrets, personal data, or local environment files are included.
- [ ] Risks, migration needs, and limitations are stated.
- [ ] The PR description distinguishes verified results from assumptions.

## Security issues

Do not publish credentials or exploit details in public issues. Until a private security contact is documented in this repository, avoid posting sensitive vulnerability details publicly; contact the repository owner through an appropriate private GitHub channel.

## Communication

Issues and pull requests should be respectful, specific, and reproducible. Include relevant logs with secrets and personal data removed.

---

BONGO · Build. Connect. Orchestrate.

# Contributing to OpenIRM

Thank you for your interest! This project is in early development and contributions are welcome.

## Quick start

1. Fork and clone the repo.
2. Install backend dependencies: `pip install -r backend/requirements.txt`
3. Install frontend dependencies: `cd frontend && npm install`
4. Copy `.env.example` to `.env` and fill in your API keys.

## Code standards

- **Python:** PEP 8. Run `black` and `ruff` before committing.
- **TypeScript:** ESLint + Prettier. Run `npm run lint && npm run format` before committing.
- **Tests:** All new features must include tests. Run `pytest` (backend) and `npm test` (frontend).
- **Commits:** Follow [Conventional Commits](https://www.conventionalcommits.org/).

## Pull request process

1. Open an issue describing the change before starting work.
2. Create a feature branch (`feat/`, `fix/`, `docs/`, etc.).
3. Submit a PR with a clear description and link to the issue.

See `docs/project_report.md` for architecture and roadmap.

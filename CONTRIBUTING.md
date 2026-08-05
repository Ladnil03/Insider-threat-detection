# Contributing to OpenIRM

Thank you for your interest in contributing to OpenIRM! We welcome contributions from the open-source community.

> [!IMPORTANT]
> **VIRTUAL ENVIRONMENT REQUIREMENT (STRICT)**:
> All backend development, script execution, linting, testing, and package installations **MUST** occur inside the Python virtual environment located at `backend/venv/`. Never install dependencies globally into your system Python.

---

## 1. Local Development Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ladnil03/Insider-threat-detection.git
cd Insider-threat-detection
```

### Step 2: Set Up Python Virtual Environment
Create the virtual environment at `backend/venv/`:
```bash
python -m venv backend/venv
```

Activate the virtual environment:
- **Windows (CMD)**:
  ```cmd
  backend\venv\Scripts\activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  backend\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS**:
  ```bash
  source backend/venv/bin/activate
  ```

Your terminal prompt should now indicate `(venv)`.

### Step 3: Install Backend Dependencies
Inside the activated virtual environment, run:
```bash
pip install -r backend/requirements.txt
```

---

## 2. Code Quality & Guidelines

- **Formatting & Linting**: We enforce `black` (line length 88) and `ruff`. Before submitting code, run:
  ```bash
  black backend/
  ruff check backend/
  ```
- **Testing**: All backend logic must include test coverage in `backend/tests/`. Run tests via:
  ```bash
  pytest backend/
  ```
- **Type Hints**: All Python functions require explicit `typing` hints and docstrings.
- **Commit Messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation updates
  - `test:` for test additions/modifications
  - `refactor:` for code cleanups
  - `chore:` for build/maintenance changes

---

## 3. Pull Request Process

1. Fork the repo and create your branch from `main`: `git checkout -b feat/your-feature-name`.
2. Ensure all tests pass and linters run cleanly.
3. Open a Pull Request with a clear description of your changes and reference any related issues.

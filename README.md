# Sample Code

## Overview

This repository contains various demo projects and sample code that demonstrate programming concepts and practical applications. The content is organized by topics such as algorithms, data structures, utility modules, and more.

---

## Project Structure

- **Algorithms**: Implementations of common algorithms such as sorting, searching, and recursion.
- **Applications**: Practical tools, scripts, and automation examples.
- **DataStructures**: Implementations of various data structures like lists, trees, stacks, queues, etc.
- **Doc**: Internal documentation, notes, and tutorial materials.
- **Stream**: Tools for working with video or data streaming.
- **tests**: Unit tests used to verify the correctness of individual modules.

---

## Installation

It is recommended to use a Python virtual environment to isolate project dependencies.

### 1. Create and activate a virtual environment

If you want uv to manage Python + virtual environments:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
```

If you prefer the standard Python tooling:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 2. Install dependencies

To run the main functionality:

```bash
uv pip install -r requirements.txt
```

To install test dependencies only:

```bash
uv pip install -r requirements-test.txt
```

> Notes:
> - `uv pip` is a drop-in replacement for `pip` that runs via uv.
> - `uv init` is for bootstrapping a **new** uv-managed project (creates
>   `pyproject.toml`/`uv.lock`). This repo already uses `requirements.txt`, so
>   `uv pip install -r ...` is the compatible path unless you migrate to uv
>   project files.

---

This project includes a GitHub Actions workflow for automated testing:

- Installs Python and test dependencies
- Runs unit tests
- Generates and uploads coverage reports

The workflow is triggered on push or pull request to the `main` branch.

---

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

You only need to install **uv**. You do **not** need to install Python manually.

### 1. Create and activate a virtual environment (uv manages Python)

**macOS/Linux:**

```bash
uv venv --python 3.10
source .venv/bin/activate
```

**Windows:**

```bash
uv venv --python 3.10
.venv\Scripts\activate
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

### 3. Run tests directly with uv (without manual Python setup)

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/ --cov=. --cov-report=term --cov-report=html
```

---

This project includes a GitHub Actions workflow for automated testing:

- Installs uv
- Uses uv-managed Python and test dependencies
- Runs unit tests
- Generates and uploads coverage reports

The workflow is triggered on push or pull request to the `main` branch.

---

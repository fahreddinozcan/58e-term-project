# API Reference: `app.app` Python Module

This page documents the importable symbols in `app/app.py`.

> **Note:** This repo is primarily an HTTP service. Most consumers should treat the HTTP routes as the public API and avoid importing internals directly.

## Module Entry Point

- File: `app/app.py`
- Direct execution entry: `if __name__ == "__main__": app.run(host="0.0.0.0", port=8080)`

## `app` (Flask application)

Defined as:

```python
app = Flask(__name__)
```

Import:

```python
from app.app import app
```

Type (runtime): `flask.Flask`

Usage example (Gunicorn):

```bash
gunicorn -b 0.0.0.0:8080 app.app:app
```

## `tasks` (in-memory task store)

Defined as:

```python
tasks = {}
```

Import:

```python
from app.app import tasks
```

Type (runtime): `dict` mapping `task_id (str)` to task `dict`.

Example: Clearing state in tests (mirrors `app/tests/test_app.py`):

```python
from app.app import tasks

tasks.clear()
```

## Route Handlers (Functions)

Each handler is a Flask view function.

> **Note:** These functions return Flask response objects produced by `jsonify(...)`. The code does not declare type hints; the “typed signature” column is inferred for documentation purposes.

| Function | Import Path | Signature (source) | Typed signature (inferred) | Return type (runtime) | Source |
|---|---|---|---|---|---|
| `hello` | `app.app:hello` | `def hello():` | `def hello() -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `health` | `app.app:health` | `def health():` | `def health() -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `get_tasks` | `app.app:get_tasks` | `def get_tasks():` | `def get_tasks() -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `create_task` | `app.app:create_task` | `def create_task():` | `def create_task() -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `get_task` | `app.app:get_task` | `def get_task(task_id):` | `def get_task(task_id: str) -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `update_task` | `app.app:update_task` | `def update_task(task_id):` | `def update_task(task_id: str) -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `delete_task` | `app.app:delete_task` | `def delete_task(task_id):` | `def delete_task(task_id: str) -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `get_stats` | `app.app:get_stats` | `def get_stats():` | `def get_stats() -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `search_tasks` | `app.app:search_tasks` | `def search_tasks():` | `def search_tasks() -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |
| `execute_command` | `app.app:execute_command` | `def execute_command():` | `def execute_command() -> flask.wrappers.Response` | `flask.wrappers.Response` | `app/app.py` |

Usage example (run the server, then call over HTTP):

```python
import requests

base = "http://localhost:8080"
resp = requests.get(f"{base}/health")
resp.raise_for_status()
print(resp.json())
```

## Deliberate “Secret” Constants

`app/app.py` defines `API_KEY` and `DATABASE_PASSWORD` with hard-coded values.

Import paths:

- `app.app:API_KEY`
- `app.app:DATABASE_PASSWORD`

> **Warning:** These exist to trigger secret-scanning tooling in CI. Do not treat them as real credentials.

Related:

- `api-reference/routes.md`
- `core-concepts/deliberate-vulnerabilities.md`

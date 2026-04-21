# Quick Reference

This page lists the public surfaces you typically interact with: HTTP routes (public API) and the importable Python module objects.

## HTTP API (Routes)

Base URL (local): `http://localhost:8080`

> **Note:** The view functions in `app/app.py` do not declare Python type hints. The “typed signature” column is an inferred, documentation-only signature based on how Flask calls the function.

| Route | Method | Handler (import path) | Signature (source) | Typed signature (inferred) | Returns | Notes |
|---|---:|---|---|---|---|
| `/` | GET | `app.app:hello` | `def hello():` | `def hello() -> flask.wrappers.Response` | JSON | Greeting message |
| `/health` | GET | `app.app:health` | `def health():` | `def health() -> flask.wrappers.Response` | JSON | Used by k8s probes |
| `/tasks` | GET | `app.app:get_tasks` | `def get_tasks():` | `def get_tasks() -> flask.wrappers.Response` | JSON | Lists all tasks |
| `/tasks` | POST | `app.app:create_task` | `def create_task():` | `def create_task() -> flask.wrappers.Response` | JSON, 201/400 | Creates a task |
| `/tasks/<task_id>` | GET | `app.app:get_task` | `def get_task(task_id):` | `def get_task(task_id: str) -> flask.wrappers.Response` | JSON, 200/404 | Fetch one task |
| `/tasks/<task_id>` | PUT | `app.app:update_task` | `def update_task(task_id):` | `def update_task(task_id: str) -> flask.wrappers.Response` | JSON, 200/400/404 | Updates fields |
| `/tasks/<task_id>` | DELETE | `app.app:delete_task` | `def delete_task(task_id):` | `def delete_task(task_id: str) -> flask.wrappers.Response` | JSON, 200/404 | Deletes task |
| `/stats` | GET | `app.app:get_stats` | `def get_stats():` | `def get_stats() -> flask.wrappers.Response` | JSON | Task metrics |
| `/search` | GET | `app.app:search_tasks` | `def search_tasks():` | `def search_tasks() -> flask.wrappers.Response` | JSON | Intentionally SQLi |
| `/execute` | POST | `app.app:execute_command` | `def execute_command():` | `def execute_command() -> flask.wrappers.Response` | JSON | Intentionally RCE |

See details: `api-reference/routes.md`.

## Python Module API

All of these are defined in `app/app.py`.

```python
from app.app import app, tasks
```

| Symbol | Import Path | Type | Description |
|---|---|---|---|
| `app` | `app.app:app` | `flask.Flask` | Flask application object |
| `tasks` | `app.app:tasks` | `dict[str, dict]` (runtime) | In-memory task store |
| `API_KEY` | `app.app:API_KEY` | `str` | Deliberate fake secret (scanner demo) |
| `DATABASE_PASSWORD` | `app.app:DATABASE_PASSWORD` | `str` | Deliberate fake secret (scanner demo) |

See details: `api-reference/python-module-app.md`.

## Repo Entry Points

- Local dev: `python app/app.py` (uses `if __name__ == "__main__": app.run(...)` in `app/app.py`).
- Container: `Dockerfile` runs `python app/app.py`.
- CI: `.github/workflows/pipeline.yaml`.
- Kubernetes deploy: `k8s/deployment.yaml` + `k8s/service.yaml`.

## Common Commands

```bash
# run tests
pytest app/tests/

# build and run container
docker build -t myapp:local .
docker run --rm -p 8080:8080 myapp:local

# apply k8s manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## CI/CD And Policy Config At A Glance

- GitHub Actions workflow: `.github/workflows/pipeline.yaml`
  - Uses Python `3.11`.
  - Runs CodeQL (Python) and Gitleaks.
  - Builds an image from `Dockerfile` and scans with Trivy.
  - Authenticates to GCP using `secrets.GCP_SA_KEY`.
  - Deploys to GKE and installs Gatekeeper.

- Gatekeeper policy:
  - Template: `k8s/gatekeeper/constraint-template.yaml`
  - Constraint: `k8s/gatekeeper/constraint.yaml` (allowed registry prefixes)

## Example: Calling From Node (No npm package)

This repo is not an npm library. If you want to use it from Node, call it over HTTP:

```js
const base = 'http://localhost:8080';

const created = await fetch(`${base}/tasks`, {
  method: 'POST',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({ title: 'From Node' })
}).then(r => r.json());

const tasks = await fetch(`${base}/tasks`).then(r => r.json());
console.log({ created, tasks });
```

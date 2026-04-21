# Guide: Run Locally

Run the Flask API directly on your machine for development and quick testing.

## Problem

You want to:

- Start the service quickly.
- Verify endpoints and run unit tests.

## Solution

### Step 1: Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Start the server

```bash
python app/app.py
```

### Step 4: Exercise the API

```bash
curl -s http://localhost:8080/ | python -m json.tool
curl -s http://localhost:8080/health | python -m json.tool
```

Expected output shape:

```json
{ "message": "Hello, security world!" }
```

### Step 5: Run tests

```bash
pytest app/tests/
```

## Troubleshooting

> **Note:** The app binds to `0.0.0.0:8080` in `app/app.py`. If port `8080` is in use, you will need to stop the other process or run the service in a container with a different host port mapping.

Common checks:

- If `curl` hangs, confirm the process is running and listening on port 8080.
- If `POST /tasks` returns `400`, confirm you sent JSON with a `title` and used `content-type: application/json`.
- If tests fail, confirm you installed the exact pinned dependencies from `requirements.txt`.

## Complete Runnable Example (Python client)

This script creates a task, updates it, then prints stats.

```python
import requests

base = "http://localhost:8080"

task = requests.post(f"{base}/tasks", json={"title": "Local run"}).json()
tid = task["id"]

requests.put(f"{base}/tasks/{tid}", json={"completed": True}).raise_for_status()
stats = requests.get(f"{base}/stats").json()

print(stats)
```

> **Note:** `requests` is not listed in `requirements.txt`. Install it for this client with `python -m pip install requests`.

<details>
<summary>Advanced Options</summary>

### Run with Gunicorn (closer to production)

`requirements.txt` includes `gunicorn`. You can start the app with:

```bash
gunicorn -b 0.0.0.0:8080 app.app:app
```

This uses the WSGI app object defined as `app = Flask(__name__)` in `app/app.py`.

### Why you might prefer Gunicorn

- The Flask dev server is single-process and primarily for development.
- Gunicorn supports multiple workers and more realistic request handling.

</details>

Related:

- `api-reference/routes.md`
- `core-concepts/http-api.md`

# Guide: Run With Docker

Use the provided `Dockerfile` to run the service in a container, matching the CI environment more closely.

## Problem

You want a reproducible runtime and a realistic image to scan (Trivy) and deploy to Kubernetes.

## Solution

### Step 1: Build the image

```bash
docker build -t myapp:local .
```

### Step 2: Run the container

```bash
docker run --rm -p 8080:8080 myapp:local
```

### Step 3: Call an endpoint

```bash
curl -s http://localhost:8080/health | python -m json.tool
```

Expected output shape:

```json
{
  "status": "healthy",
  "timestamp": "<utc isoformat>"
}
```

## Complete Runnable Example (Build + Smoke Test)

This sequence builds, runs in the background, exercises a couple endpoints, then stops the container.

### Step 1: Build

```bash
docker build -t myapp:local .
```

### Step 2: Run in the background

```bash
docker run -d --rm --name myapp -p 8080:8080 myapp:local
```

### Step 3: Create a task and list tasks

```bash
curl -s -X POST http://localhost:8080/tasks \
  -H 'content-type: application/json' \
  -d '{"title":"Container task"}' | python -m json.tool

curl -s http://localhost:8080/tasks | python -m json.tool
```

### Step 4: Stop

```bash
docker stop myapp
```

## What The Dockerfile Does (Source Walk)

`Dockerfile`:

- Uses `python:alpine` as a small base.
- Copies `requirements.txt` and installs dependencies.
- Copies `app/` into the image.
- Exposes port `8080`.
- Starts the server with `python app/app.py`.

> **Warning:** `python:alpine` uses musl libc; some Python packages compile differently than on Debian-based images. For production, choose a base image aligned with your dependency needs.

## Advanced: Run with Gunicorn

`requirements.txt` includes `gunicorn`, but the container command uses the Flask dev server. You can run Gunicorn instead:

```bash
docker run --rm -p 8080:8080 myapp:local \
  gunicorn -b 0.0.0.0:8080 app.app:app
```

Trade-offs:

- Gunicorn is closer to production and handles concurrency better.
- The Flask dev server is simpler and fine for demos.

<details>
<summary>Advanced Options</summary>

### Map to a different host port

If host port 8080 is already in use:

```bash
docker run --rm -p 18080:8080 myapp:local
curl -s http://localhost:18080/health | python -m json.tool
```

### Why the CI image scan matters

The workflow in `.github/workflows/pipeline.yaml` scans the built image with Trivy. Running locally with Docker helps you reproduce the exact base image (`python:alpine`) and dependency set that Trivy evaluates.

</details>

Related:

- `core-concepts/devsecops-pipeline.md`

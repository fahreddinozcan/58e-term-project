# Getting Started

This repository is a small Flask-based Task Management REST API that is intentionally paired with CI/CD, security scanning, and Kubernetes policy enforcement to demonstrate a DevSecOps pipeline end-to-end.

## The Problem

- You need a realistic-but-small service to exercise CI steps like tests, linting, and coverage.
- You want security tools (SAST, secret scanning, container scanning, IaC scanning) to produce findings you can triage.
- You want a deploy pipeline that pushes an image and deploys to Kubernetes with guardrails.
- You need a repeatable example of “policy blocks unsafe deploys” (OPA Gatekeeper) instead of relying on manual review.

## The Solution

The project combines:

- A Flask API (`app/app.py`) with CRUD endpoints for tasks.
- Deliberate insecure patterns (fake secrets, SQL injection, command injection) to validate scanners.
- A GitHub Actions workflow (`.github/workflows/pipeline.yaml`) that runs tests, CodeQL, Gitleaks, Trivy, and (optionally) Checkov.
- Kubernetes manifests (`k8s/`) plus an OPA Gatekeeper constraint that only allows images from an approved registry prefix.

Quick taste (run locally, then hit health):

```bash
python -m pip install -r requirements.txt
python app/app.py
curl -s http://localhost:8080/health | python -m json.tool
```

Expected output shape:

```json
{
  "status": "healthy",
  "timestamp": "2026-04-21T12:34:56.789123"
}
```

## Installation

### Python (supported)

### Step 1: Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Node package managers (not applicable)

This repository is not published as an npm package and does not include `package.json`, so these are intentionally not supported:

```bash
npm install
pnpm add
yarn add
bun add
```

If you need a Node-based wrapper, treat this service as an HTTP dependency and call it over the network.

## Quick Start

### Step 1: Start the API

```bash
python app/app.py
```

By default, the server listens on `0.0.0.0:8080` (see `app/app.py`).

### Step 2: Create a task

```bash
curl -s -X POST http://localhost:8080/tasks \
  -H 'content-type: application/json' \
  -d '{"title":"Write docs","description":"Generate .md docs"}' | python -m json.tool
```

Expected output shape:

```json
{
  "id": "<uuid>",
  "title": "Write docs",
  "description": "Generate .md docs",
  "completed": false,
  "created_at": "<iso timestamp>"
}
```

### Step 3: List tasks

```bash
curl -s http://localhost:8080/tasks | python -m json.tool
```

## Key Features

- RESTful task CRUD endpoints plus stats (`app/app.py`).
- Health checking for k8s probes (`GET /health`).
- GitHub Actions DevSecOps workflow (tests + CodeQL + Gitleaks + Trivy + optional Checkov) in `.github/workflows/pipeline.yaml`.
- Kubernetes deployment/service manifests in `k8s/`.
- OPA Gatekeeper policy to restrict allowed image registries (`k8s/gatekeeper/constraint-template.yaml`, `k8s/gatekeeper/constraint.yaml`).

> **Warning:** `app/app.py` contains deliberate secrets and vulnerabilities (for scanner demonstrations). Do not deploy this code as-is to an untrusted environment. See `core-concepts/deliberate-vulnerabilities.md`.

Next reads:

- `architecture.md`
- `api-reference/routes.md`
- `guides/run-with-docker.md`

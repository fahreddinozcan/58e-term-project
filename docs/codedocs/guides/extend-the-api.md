# Guide: Extend The API Safely

Add new endpoints or evolve the data model while keeping tests and security checks meaningful.

## Problem

You want to add real features (auth, persistence, filtering) without turning the project into an unmaintainable demo.

## Solution

### Step 1: Pick a change that preserves the learning goals

Good extensions:

- Add pagination/filtering to `GET /tasks`.
- Add a new field (e.g. `due_date`) with validation.
- Replace the in-memory dict with SQLite on disk (and then show how replicas behave).

### Step 2: Implement the endpoint in `app/app.py`

Example: add server-side filtering by completion state.

```python
@app.route("/tasks", methods=["GET"])
def get_tasks():
    completed = request.args.get("completed")
    all_tasks = list(tasks.values())

    if completed is None:
        return jsonify({"tasks": all_tasks})

    want = completed.lower() in ("1", "true", "yes")
    filtered = [t for t in all_tasks if bool(t.get("completed")) is want]
    return jsonify({"tasks": filtered})
```

### Step 3: Add/adjust tests

Update `app/tests/test_app.py` to cover the new behavior via HTTP calls.

### Step 4: Keep security checks “real”

- Replace intentional vulnerabilities with safer patterns if you plan to run this service beyond a sandbox.
- If you remove the deliberate insecure endpoints, update your pipeline expectations (CodeQL/Gitleaks findings will change).

## Complete Runnable Example

After adding filtering, you can run:

```bash
curl -s -X POST http://localhost:8080/tasks \
  -H 'content-type: application/json' \
  -d '{"title":"A","completed":false}'

curl -s -X POST http://localhost:8080/tasks \
  -H 'content-type: application/json' \
  -d '{"title":"B","completed":true}'

curl -s "http://localhost:8080/tasks?completed=true" | python -m json.tool
```

> **Warning:** As written, `create_task()` ignores a client-provided `completed` field and always sets `completed: False`. If you want client-controlled completion at create time, change `create_task()` carefully and add tests.

## Trade-offs

- Adding persistence improves realism but adds operational overhead (migrations, backup, concurrency).
- Adding auth increases security realism but can distract from the pipeline focus; keep it minimal (e.g. a static token) unless auth is the core lesson.
- Removing intentional vulnerabilities makes the service safer, but it reduces the “always has findings” property that is useful when teaching scanners.

Related:

- `core-concepts/task-store.md`
- `api-reference/python-module-app.md`

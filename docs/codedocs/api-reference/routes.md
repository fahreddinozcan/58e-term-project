# API Reference: HTTP Routes

All routes are implemented in `app/app.py` using Flask.

Base URL (local): `http://localhost:8080`

> **Warning:** `/search` and `/execute` are intentionally vulnerable and exist for security-scanner demonstrations. Do not expose them publicly.

## Data Model: Task

Task objects are plain JSON dictionaries created by `app/app.py:create_task`.

Example:

```json
{
  "id": "2f2d2e7c-1a2b-4c3d-8e9f-0123456789ab",
  "title": "Example",
  "description": "",
  "completed": false,
  "created_at": "2026-04-21T12:34:56.789123",
  "updated_at": "2026-04-21T12:35:10.000000"
}
```

## `GET /`

- Source: `app/app.py` (`def hello():`)
- Returns: `200 OK`

```json
{ "message": "Hello, security world!" }
```

## `GET /health`

- Source: `app/app.py` (`def health():`)
- Returns: `200 OK`
- Used by: `k8s/deployment.yaml` liveness/readiness probes.

Response:

```json
{ "status": "healthy", "timestamp": "<utc isoformat>" }
```

## `GET /tasks`

- Source: `app/app.py` (`def get_tasks():`)
- Returns: `200 OK`

Response:

```json
{ "tasks": [ {"id":"...", "title":"..."} ] }
```

Example:

```bash
curl -s http://localhost:8080/tasks | python -m json.tool
```

## `POST /tasks`

- Source: `app/app.py` (`def create_task():`)

Request body:

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `title` | `string` | — | Task title (required) |
| `description` | `string` | `""` | Optional description |

Returns:

- `201 Created` with task JSON
- `400 Bad Request` with `{"error": "Title is required"}` if missing

Example:

```bash
curl -s -X POST http://localhost:8080/tasks \
  -H 'content-type: application/json' \
  -d '{"title":"Write report"}' | python -m json.tool
```

## `GET /tasks/<task_id>`

- Source: `app/app.py` (`def get_task(task_id):`)
- Path params:

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `task_id` | `string` | — | UUID string returned by `POST /tasks` |

Returns:

- `200 OK` with task JSON
- `404 Not Found` with `{"error": "Task not found"}`

## `PUT /tasks/<task_id>`

- Source: `app/app.py` (`def update_task(task_id):`)

Request body (partial update):

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `title` | `string` | — | New title |
| `description` | `string` | — | New description |
| `completed` | `boolean` | — | Completion flag |

Returns:

- `200 OK` with updated task
- `404 Not Found` if missing
- `400 Bad Request` with `{"error": "No data provided"}` if JSON body is empty/invalid

Example:

```bash
curl -s -X PUT http://localhost:8080/tasks/<id> \
  -H 'content-type: application/json' \
  -d '{"completed":true}' | python -m json.tool
```

## `DELETE /tasks/<task_id>`

- Source: `app/app.py` (`def delete_task(task_id):`)

Returns:

- `200 OK` with `{"message":"Task deleted","task":{...}}`
- `404 Not Found` if missing

## `GET /stats`

- Source: `app/app.py` (`def get_stats():`)

Returns task metrics:

```json
{
  "total_tasks": 2,
  "completed_tasks": 1,
  "completion_rate": 0.5,
  "server_time": "<iso timestamp>"
}
```

## `GET /search?q=<keyword>` (Intentionally Vulnerable)

- Source: `app/app.py` (`def search_tasks():`)
- Query params:

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `q` | `string` | `""` | Search keyword |

Internals:

- Builds an in-memory SQLite table and inserts current tasks.
- Uses string interpolation to construct the SQL query, making it vulnerable to injection.

Response:

```json
{ "results": [["id","title","description"], ...] }
```

> **Warning:** Do not copy this pattern. Use parameterized queries.

## `POST /execute` (Intentionally Vulnerable)

- Source: `app/app.py` (`def execute_command():`)

Request body:

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `command` | `string` | `""` | Shell command string |

Response:

```json
{ "result": 0 }
```

> **Warning:** This is a command injection / RCE vulnerability (`os.system`). Never expose this endpoint.

Related:

- `core-concepts/http-api.md`
- `core-concepts/deliberate-vulnerabilities.md`

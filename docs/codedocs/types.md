# Types

This repository does not export TypeScript types or interfaces.

The primary public interfaces are:

- HTTP endpoints (documented in `api-reference/routes.md`).
- A Python module (`app/app.py`) that defines the Flask `app` object (documented in `api-reference/python-module-app.md`).

Even without TypeScript exports, the API still has stable *shapes* you can treat as types in your own codebase.

## Runtime Shapes You Can Type

### `Task` JSON shape (produced by `app/app.py:create_task`)

The server constructs tasks as a plain dict with these keys:

- `id: string` (UUID)
- `title: string`
- `description: string` (defaults to `""`)
- `completed: boolean` (defaults to `false` at creation time)
- `created_at: string` (ISO timestamp)
- `updated_at?: string` (ISO timestamp, present after updates)

This is visible in `app/app.py` where `create_task()` builds `new_task` and `update_task()` adds `updated_at`.

### Common response envelopes

These routes consistently wrap data in small envelopes:

- `GET /tasks` returns `{ "tasks": Task[] }` (see `app/app.py:get_tasks`).
- `GET /stats` returns a stats object with `total_tasks`, `completed_tasks`, `completion_rate`, `server_time` (see `app/app.py:get_stats`).
- Error cases return `{ "error": string }` for the main CRUD flows.

> **Note:** The code is intentionally minimal and does not enforce strict typing at runtime (no Pydantic, Marshmallow, etc.). Client code should validate inputs if it depends on stronger guarantees.

## Suggested Client Types (Not Exported)

Use these in your own project if you want stronger tooling support.

### TypeScript

```ts
export type Task = {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at?: string;
};

export type TasksResponse = { tasks: Task[] };

export type StatsResponse = {
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  server_time: string;
};

export type ErrorResponse = { error: string };
```

### Python (dataclasses)

```python
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: Optional[str] = None
```

## Generating Types Properly (OpenAPI)

If you want types that are guaranteed to stay in sync, the usual approach is to define an OpenAPI spec for the routes (based on `api-reference/routes.md`) and then generate:

- TypeScript clients (e.g. `openapi-typescript`, `orval`, `openapi-generator`).
- Python clients and models.

This repo does not currently include an OpenAPI document; the authoritative definitions are the route handlers in `app/app.py`.

If you want typed client code, a practical approach is to:

1) Define an OpenAPI spec for the routes.
2) Generate a typed client (TypeScript/Python) from that spec.

See `guides/extend-the-api.md` for a suggested direction.

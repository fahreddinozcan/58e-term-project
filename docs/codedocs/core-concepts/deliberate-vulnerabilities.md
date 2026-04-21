# Deliberate Vulnerabilities (Scanner Demonstrations)

This project contains intentionally insecure code paths and fake secrets so that DevSecOps tools produce findings you can validate in CI.

## What It Is And Why It Exists

The goal is not to build a secure task service; it is to build a small target that exercises:

- Secret scanning (Gitleaks)
- Static analysis for injection bugs (CodeQL)
- Container scanning (Trivy)
- Admission policy enforcement (Gatekeeper)

The “bad parts” are concentrated in `app/app.py` and are called out with comments.

## How It Relates To Other Concepts

- `.github/workflows/pipeline.yaml` runs Gitleaks and CodeQL that should flag these issues.
- The API reference (`api-reference/routes.md`) documents these endpoints as unsafe and demo-only.

## What’s In The Code (With File References)

### Fake secrets (secret scanning)

`app/app.py` defines:

- `API_KEY = "sk_live_..."`
- `DATABASE_PASSWORD = "super_secret_password123!"`

These are intentionally present to trigger Gitleaks.

### SQL injection (SAST)

`GET /search` in `app/app.py:search_tasks` builds a SQL query using f-string interpolation:

```python
query = f"SELECT * FROM tasks WHERE title LIKE '%{keyword}%' OR description LIKE '%{keyword}%'"
cursor.execute(query)
```

This is a classic SQL injection pattern; the correct approach is parameterized queries.

### Command injection / RCE (SAST)

`POST /execute` in `app/app.py:execute_command` uses:

```python
result = os.system(command)
```

Executing user-provided strings is intentionally unsafe and should be flagged.

## Examples

### Basic: Observe the unsafe endpoints (do not run against real systems)

```bash
curl -s "http://localhost:8080/search?q=test" | python -m json.tool
curl -s -X POST http://localhost:8080/execute \
  -H 'content-type: application/json' \
  -d '{"command":"echo hello"}' | python -m json.tool
```

### Advanced: Make scanners “light up” in CI

- CodeQL should report issues related to SQL injection and command execution in `app/app.py`.
- Gitleaks should detect the `API_KEY` and `DATABASE_PASSWORD` literals.

You can validate the pipeline wiring by opening the Security tab in GitHub and checking SARIF results.

> **Warning:** Never reuse patterns from this file in production code. The insecure endpoints exist solely to validate that your DevSecOps pipeline detects and blocks risky changes.

## Trade-offs

**Educational value vs accidental exposure.** Keeping vulnerabilities in the main branch is great for teaching because it guarantees scanners will find something and you can demonstrate the full workflow (detection, triage, gating). The risk is that someone may deploy this service outside a controlled environment, especially because the repo includes `Dockerfile` and Kubernetes manifests. If that happens, the “demo-only” vulnerabilities become real attack surfaces. Treat this code as unsafe by default and keep deployments restricted to isolated labs.

**Tool validation vs signal quality.** Intentionally bad patterns provide predictable findings, which is useful when validating that CodeQL and Gitleaks are wired correctly in `.github/workflows/pipeline.yaml`. But if you expand the codebase, the constant presence of known issues can reduce trust in the results and make it harder to spot new regressions. In real projects, teams aim for a low-noise baseline so that a new finding is meaningful and actionable. If you keep the demo vulnerabilities, consider isolating them (separate branch, separate endpoint group, or explicit suppression with documentation).

**Demo simplicity vs realistic mitigation.** It’s easy to say “replace `os.system`” or “parameterize SQL,” and those are important fixes. However, real mitigation is usually layered: authorization to restrict who can call an endpoint, input validation to constrain values, safer APIs by default, and runtime controls (least privilege, seccomp, network policies). This repo’s value is that it shows the *shape* of the risk and the scanner output. If you evolve this into something deployable, redesign the endpoints rather than applying minimal patches.

Related:

- `core-concepts/devsecops-pipeline.md`
- `api-reference/routes.md`

# DevSecOps Pipeline (GitHub Actions)

The workflow in `.github/workflows/pipeline.yaml` is the “spine” of this repo: it takes the small Flask service and wraps it in quality checks, security scans, container build, and Kubernetes deployment.

## What It Is And Why It Exists

The pipeline is triggered on pushes and pull requests to `main`/`master`. It exists to demonstrate:

- “Shift-left” testing before security scanning.
- Automated security scanning across code, secrets, IaC, and container images.
- Deploy-time enforcement via OPA Gatekeeper.

## How It Relates To Other Concepts

- CodeQL and Gitleaks are expected to flag patterns intentionally present in `app/app.py`.
- Trivy scans the image built from `Dockerfile`.
- Checkov scans the `terraform/` directory (but see the note about `terraform/main.txt`).
- Gatekeeper policies in `k8s/gatekeeper/` can block deployments based on image registry.

## How It Works Internally (Workflow Walk)

The workflow has four jobs:

1) `build-and-test`
   - Sets up Python 3.11.
   - Installs dependencies from `requirements.txt`.
   - Runs `pytest app/tests/`.
   - Linting via pylint is present but commented out.

2) `security-scan` (depends on tests)
   - Initializes CodeQL for Python.
   - Runs CodeQL analysis.
   - Runs Gitleaks secret scanning.
   - Conditionally runs Checkov if a `terraform/` directory exists.

3) `build-image` (depends on security scan)
   - Builds Docker image `myapp:${{ github.sha }}`.
   - Runs Trivy with `exit-code: 1` for `CRITICAL,HIGH` vulnerabilities.
   - Authenticates to Google Cloud using `secrets.GCP_SA_KEY`.
   - Tags and pushes the image to GAR.

4) `deploy-to-k8s` (depends on build)
   - Authenticates to Google Cloud and fetches GKE credentials.
   - Installs Gatekeeper and waits for readiness.
   - Patches the Gatekeeper constraint (`k8s/gatekeeper/constraint.yaml`) and deployment image (`k8s/deployment.yaml`) using `sed`.
   - Applies the manifests.
   - Verifies that Gatekeeper did not block the deployment.

```mermaid
flowchart TD
  A[push / PR] --> B[build-and-test]
  B --> C[security-scan]
  C --> D[build-image]
  D --> E[deploy-to-k8s]

  C --> C1[CodeQL]
  C --> C2[Gitleaks]
  C --> C3[Checkov (optional)]
  D --> D1[Trivy]
  E --> E1[Gatekeeper template+constraint]
  E --> E2[k8s apply]
```

## Configuration (Secrets And Inputs)

The workflow expects these GitHub Secrets:

- `GCP_SA_KEY`: JSON key for a Google Cloud service account.
- `GCP_PROJECT_ID`: project id used in GAR image tags.
- `GKE_CLUSTER_NAME`: GKE cluster name.
- `GKE_ZONE`: GKE zone.
- `GITLEAKS_LICENSE`: license key if required by your Gitleaks configuration.

See also IAM guidance snippets in `README.md`.

## Examples

### Basic: Run the “build-and-test” steps locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest app/tests/
```

### Advanced: Preview what Gatekeeper will reject

In `k8s/deployment.yaml`, there is a commented failure scenario:

```yaml
# image: docker.io/library/python:3.9-slim
```

If you deploy with that image while the constraint only allows your GAR prefix, Gatekeeper should block creation.

> **Warning:** The pipeline edits YAML files in-place using `sed` (`.github/workflows/pipeline.yaml`). That makes the workflow stateful and can leave modified files in the workspace during CI steps. Prefer templating (kustomize/helm) for long-lived production pipelines.

## Trade-offs

**Fast feedback vs completeness.** `.github/workflows/pipeline.yaml` demonstrates a broad set of security checks (CodeQL, Gitleaks, Trivy, Checkov) without heavy configuration. That makes it quick to adopt and easy to understand, which is ideal for a term project. The flip side is that defaults may be noisy or may miss project-specific risks until you tune rule sets, add baselines, and define ownership for findings. In mature pipelines, you also add caching, parallelism, and staged enforcement to keep feedback fast while still being thorough.

**Checkov soft-fail vs enforcement.** The Checkov step is configured with `soft_fail: true`, which means issues are reported (including SARIF upload) but they do not block the job. That’s often the right first step when introducing IaC scanning because it avoids halting delivery while teams learn how to fix findings. The trade-off is that “known-bad” IaC can still ship unless humans intervene. If the goal is prevention rather than visibility, switch to hard-fail and make sure the Terraform code is actually scanned (see the note about `terraform/main.txt`).

**In-place YAML mutation vs robustness.** The deploy job uses `sed` to rewrite `k8s/gatekeeper/constraint.yaml` and `k8s/deployment.yaml` with project-specific values. This is straightforward, but it is brittle: small YAML formatting changes can break the replacement, and the workflow becomes harder to test locally. Tools like kustomize (already present via `k8s/kustomization.yaml`) let you set images and parameters declaratively and reduce string-based patching. For production-grade pipelines, prefer manifests generated from templates/overlays and keep the committed YAML immutable.

Related:

- `core-concepts/policy-enforcement.md`
- `core-concepts/deliberate-vulnerabilities.md`

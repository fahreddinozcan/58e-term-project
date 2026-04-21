# Guide: Customize The Gatekeeper Image Allowlist

Adjust the allowed container registries enforced by Gatekeeper.

## Problem

You need to allow images from different registries (for example, a new Artifact Registry repo, or a shared base image registry) without disabling policy enforcement.

## Solution

The allowlist is configured in `k8s/gatekeeper/constraint.yaml` under `spec.parameters.repos`.

### Step 1: Edit the constraint

Example allowing two prefixes:

```yaml
parameters:
  repos:
    - "europe-west1-docker.pkg.dev/my-project/myapp-repo/"
    - "europe-west1-docker.pkg.dev/my-project/base-images/"
```

### Step 2: Apply the updated constraint

```bash
kubectl apply -f k8s/gatekeeper/constraint.yaml
```

### Step 3: Test allowed and denied images

1) Set an allowed image in `k8s/deployment.yaml` and apply.
2) Set a disallowed image (e.g. `docker.io/library/python:3.9-slim`) and apply.

## How The Policy Evaluates Images (Internals)

The core logic is in `k8s/gatekeeper/constraint-template.yaml`:

- For each container image, it checks `startswith(image, registry)` for any `registry` in `input.parameters.repos`.
- If no allowed prefix matches, it emits a `violation` message.

> **Note:** Prefix matching means `europe-west1-docker.pkg.dev/.../myapp-repo/` will allow any tag under that path, but it does not enforce digest pinning.

## Complete Runnable Example (CI-style patch)

The CI workflow uses a placeholder replacement pattern (see `.github/workflows/pipeline.yaml`). You can replicate it:

```bash
REGISTRY="europe-west1-docker.pkg.dev/<project>/myapp-repo"
sed -i "" "s|<REGISTRY_PLACEHOLDER>|$REGISTRY|g" k8s/gatekeeper/constraint.yaml
kubectl apply -f k8s/gatekeeper/constraint.yaml
```

> **Warning:** The current `k8s/gatekeeper/constraint.yaml` in this repo does not include `<REGISTRY_PLACEHOLDER>` (it has a concrete value). If you want this patching approach, update the file to use a placeholder consistently.

## Trade-offs

- Broader allowlists reduce friction but weaken the control; tight allowlists strengthen control but require more maintenance.
- Prefix-based allowlists are easy to reason about but cannot express “only image X by digest”.
- Policy changes affect developer velocity; document the process for requesting allowlist updates.

Related:

- `core-concepts/policy-enforcement.md`

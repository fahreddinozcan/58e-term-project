# Guide: Deploy To GKE With Gatekeeper

Deploy the service to Google Kubernetes Engine (GKE) using the manifests in `k8s/` and the Gatekeeper policy in `k8s/gatekeeper/`.

## Problem

You want a real deployment target with:

- An image hosted in Artifact Registry.
- Admission control enforcing that only approved images are deployed.

## Solution

This repo’s CI pipeline already includes deployment steps (see `.github/workflows/pipeline.yaml`). This guide outlines the same flow manually.

### Step 1: Build and push an image to Artifact Registry

```bash
export PROJECT_ID="<your-project>"
export REGION="europe-west1"
export REPO="myapp-repo"

gcloud auth configure-docker ${REGION}-docker.pkg.dev

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/myapp:manual"
docker build -t "$IMAGE" .
docker push "$IMAGE"
```

### Step 2: Install Gatekeeper

```bash
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml
kubectl wait --for=condition=available --timeout=300s deployment/gatekeeper-controller-manager -n gatekeeper-system
```

### Step 3: Apply the constraint template and constraint

Update `k8s/gatekeeper/constraint.yaml` to allow your registry prefix (or patch it the way CI does), then apply:

```bash
kubectl apply -f k8s/gatekeeper/constraint-template.yaml
kubectl apply -f k8s/gatekeeper/constraint.yaml
```

### Step 4: Deploy the service

Update `k8s/deployment.yaml` to point at your pushed image, then:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Step 5: Verify probes and traffic

```bash
kubectl get pods -l app=myapp
kubectl get svc myapp-service
```

## Complete Runnable Example (Kustomize)

`k8s/kustomization.yaml` defines an image override. If you prefer kustomize:

```bash
cd k8s
kustomize edit set image myapp=${IMAGE}
kubectl apply -k .
```

> **Warning:** The repository’s CI deploy step uses `sed` to patch YAML in-place. If you run the workflow locally (or reuse the workspace), you can end up with modified manifests. Prefer kustomize overlays or Helm for long-term maintainability.

## Note About Terraform Scanning

`terraform/main.txt` contains Terraform configuration, but it is not named with a `.tf` extension. The CI job runs Checkov against the `terraform/` directory; to ensure it is scanned as Terraform, rename to `terraform/main.tf`.

Related:

- `core-concepts/policy-enforcement.md`
- `core-concepts/devsecops-pipeline.md`

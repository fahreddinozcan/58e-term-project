#!/bin/bash
# Script to install OPA Gatekeeper on GKE cluster

set -e

# Load environment variables
source .env

# Authenticate with GKE cluster
gcloud container clusters get-credentials $GKE_CLUSTER_NAME --zone $GKE_ZONE --project $GCP_PROJECT_ID

# Install OPA Gatekeeper using Helm
echo "Installing OPA Gatekeeper..."
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.12/deploy/gatekeeper.yaml

# Wait for Gatekeeper to be ready
echo "Waiting for Gatekeeper to be ready..."
kubectl wait --for=condition=ready pod -l control-plane=controller-manager -n gatekeeper-system --timeout=300s

# Apply Gatekeeper policies
echo "Applying Gatekeeper policies..."
kubectl apply -f k8s/gatekeeper/constraint-template.yaml
kubectl apply -f k8s/gatekeeper/constraint.yaml

echo "OPA Gatekeeper installation complete!"

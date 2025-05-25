# 58e-term-project

```
 ~/De/2/cmpe58e/58e-term-project │ master  kubectl create clusterrolebinding github-deployer-admin \                         ✔ │ 10s │ devsecops 󱃾
  --clusterrole=cluster-admin \
  --user=github-actions-deployer@cmpe-58e-term-project.iam.gserviceaccount.com
clusterrolebinding.rbac.authorization.k8s.io/github-deployer-admin created
```

---

```
# 1. Add required IAM roles to your service account
export SERVICE_ACCOUNT_EMAIL="github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com"
export PROJECT_ID="YOUR_PROJECT_ID"

# Grant Kubernetes Engine Admin role (includes cluster admin permissions)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/container.admin"

# Grant Security Admin role for security policies
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/iam.securityAdmin"

# Alternative: Grant more granular permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/container.clusterAdmin"

# Verify the permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$SERVICE_ACCOUNT_EMAIL"
```

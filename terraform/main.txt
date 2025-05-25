provider "google" {
  project = "cmpe-58e-term-project"
  region  = "us-central1"
  zone    = "us-central1-a"
}

# Secure GKE cluster configuration
resource "google_container_cluster" "primary" {
  name     = "devsecops-cluster"
  location = "us-central1-a"

  # Use a regional cluster with multiple zones for high availability
  # Recommended for production workloads
  # location = "us-central1"
  # node_locations = ["us-central1-a", "us-central1-b", "us-central1-c"]

  # BREAK IaC SECURITY CHECK: Uncomment to disable network policy (Checkov will flag this)
  # network_policy {
  #   enabled = false
  # }

  # BREAK IaC SECURITY CHECK: Uncomment to disable private cluster (Checkov will flag this)
  # private_cluster_config {
  #   enable_private_nodes    = false
  #   enable_private_endpoint = false
  # }

  # BREAK IaC SECURITY CHECK: Uncomment to disable master auth network config (Checkov will flag this)
  # master_authorized_networks_config {
  #   # Empty block means allow all IPs to access the cluster
  # }

  # Remove the default node pool and create a custom one
  remove_default_node_pool = true
  initial_node_count       = 1

  # BREAK IaC SECURITY CHECK: Uncomment to disable workload identity (Checkov will flag this)
  # workload_identity_config {
  #   # Empty block means workload identity is not configured
  # }

  # Enable Kubernetes Network Policy
  network_policy {
    enabled  = true
    provider = "CALICO"
  }

  # Enable private cluster
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Enable master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "10.0.0.0/8"
      display_name = "internal-network"
    }
  }

  # Enable workload identity
  workload_identity_config {
    workload_pool = "cmpe-58e-term-project.svc.id.goog"
  }
}

# Node pool with secure configuration
resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-node-pool"
  location   = "us-central1-a"
  cluster    = google_container_cluster.primary.name
  node_count = 2

  # BREAK IaC SECURITY CHECK: Uncomment to enable auto-repair but disable auto-upgrade (Checkov will flag this)
  # management {
  #   auto_repair  = true
  #   auto_upgrade = false
  # }

  # Auto-scaling configuration
  autoscaling {
    min_node_count = 1
    max_node_count = 3
  }

  # Node configuration
  node_config {
    machine_type = "e2-standard-2"

    # BREAK IaC SECURITY CHECK: Uncomment to use default service account (Checkov will flag this)
    # service_account = "default"

    # Google recommends custom service accounts with minimal permissions
    service_account = "github-actions-deployer@cmpe-58e-term-project.iam.gserviceaccount.com"

    # Enable workload identity on the node pool
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # BREAK IaC SECURITY CHECK: Uncomment to enable privileged containers (Checkov will flag this)
    # metadata = {
    #   "disable-legacy-endpoints" = "true"
    #   "allow-privileged"         = "true"
    # }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Enable secure boot for nodes
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  # Enable auto-repair and auto-upgrade
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "myapp_repo" {
  location      = "europe-west1"
  repository_id = "myapp-repo"
  format        = "DOCKER"

  # BREAK IaC SECURITY CHECK: Uncomment to disable CMEK (Checkov will flag this)
  # kms_key_name = null
}

# IAM for GitHub Actions deployer service account
resource "google_service_account" "github_actions_deployer" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployer"
}

# Grant necessary roles to the service account
resource "google_project_iam_member" "container_admin" {
  project = "cmpe-58e-term-project"
  role    = "roles/container.admin"
  member  = "serviceAccount:${google_service_account.github_actions_deployer.email}"
}

resource "google_project_iam_member" "artifact_admin" {
  project = "cmpe-58e-term-project"
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${google_service_account.github_actions_deployer.email}"
}

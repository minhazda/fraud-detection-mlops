output "service_url" {
  value = google_cloud_run_v2_service.api.uri
}

output "artifact_registry" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}

output "gcp_wif_provider" {
  value = google_iam_workload_identity_pool_provider.github.name
}

output "gcp_deploy_sa" {
  value = google_service_account.deployer.email
}

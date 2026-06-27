variable "project_id" {
  type        = string
  description = "GCP project ID to deploy into."
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "service_name" {
  type    = string
  default = "fraud-detection-api"
}

variable "repository_id" {
  type    = string
  default = "fraud-detection"
}

variable "image" {
  type        = string
  description = "Artifact Registry image ref to deploy (built during bootstrap)."
}

variable "min_instances" {
  type    = number
  default = 0
}

variable "max_instances" {
  type    = number
  default = 2
}

variable "github_repo" {
  type    = string
  default = "minhazda/fraud-detection-mlops"
}

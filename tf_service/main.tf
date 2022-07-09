# Terraform

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.18.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Parameters

data "aws_caller_identity" "current" {}

locals {
  project_name    = "the-spymaster-backend"
  service_name    = "${local.project_name}-${var.env}"
  aws_account_id  = data.aws_caller_identity.current.account_id
  project_root    = "${path.module}/.."
  lambda_zip_name = "service.zip"
  layer_zip_name  = "layer.zip"
  # Secrets
  kms_env_map     = {
    "dev" : "arn:aws:kms:us-east-1:096386908883:key/59b86867-2b0d-4d48-bdee-87bdbf1e249a",
  }
  kms_arn           = local.kms_env_map[var.env]
  # Domain
  base_app_domain   = "the-spymaster.xyz"
  hosted_zone_id    = "Z0770508EK6R7V32364I"
  certificate_arn   = "arn:aws:acm:us-east-1:096386908883:certificate/fc0faea8-e891-438a-a779-4013ee38755f"
  domain_suffix_map = {
    "dev"     = "dev."
    "staging" = ""
    "prod"    = ""
  }
  domain_suffix  = local.domain_suffix_map[var.env]
  backend_domain = "backend.${local.domain_suffix}${local.base_app_domain}"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "env" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "stage", "prod"], var.env)
    error_message = "Valid values for var: `dev`, `stage`, `prod`"
  }
}

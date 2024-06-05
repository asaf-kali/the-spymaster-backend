# Terraform

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.12.0"
    }
  }
  backend "s3" {
    bucket               = "the-spymaster-infra-tf-state"
    key                  = "backend/terraform.tfstate"
    region               = "us-east-1"
    dynamodb_table       = "the-spymaster-infra-tf-state-lock"
    workspace_key_prefix = "env"
  }
}

provider "aws" {
  region = var.aws_region
}

# Parameters

variable "aws_region" {
  default = "us-east-1"
}

variable "sentry_dsn" {
  type      = string
  sensitive = true
}

locals {
  #  Environment
  env_map = {
    "default" = "dev"
    "prod"    = "prod"
  }
  env = local.env_map[terraform.workspace]
  # Base
  project_name    = "the-spymaster-backend"
  service_name    = "${local.project_name}-${local.env}"
  aws_account_id = data.aws_caller_identity.current.account_id
  # Paths
  tf_root = abspath(path.module)
  project_root = abspath("${path.module}/../")
  layer_src_root  = "${local.project_root}/.deployment/layer-dependencies"
  lambda_src_root = "${local.project_root}/service/"
  # Domain
  base_app_domain = "303707.xyz"
  hosted_zone_id  = "Z0883104W79ZV11TF62Q"
  certificate_id  = "7c013d7d-0ff5-45df-97a8-c34019e44bdb"
  certificate_arn = "arn:aws:acm:us-east-1:${local.aws_account_id}:certificate/${local.certificate_id}"
  domain_suffix_map = {
    "dev"     = "dev."
    "staging" = ""
    "prod"    = ""
  }
  domain_suffix   = local.domain_suffix_map[local.env]
  backend_domain = "backend.${local.domain_suffix}${local.base_app_domain}"
  # Encryption
  default_key_arn = "arn:aws:kms:us-east-1:${local.aws_account_id}:key/0b9c713c-1c4b-43ad-84df-1f62117838f0"
}

data "aws_caller_identity" "current" {}

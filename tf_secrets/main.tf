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

locals {
  project_name = "the-spymaster-backend"
  service_name = "${local.project_name}-${var.env}"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "env" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "stage", "prod"], var.env)
    error_message = "Valid values for env: `dev`, `stage`, `prod`"
  }
}

variable "sentry_dsn" {
  type      = string
  sensitive = true
}


variable "db_password" {
  type      = string
  sensitive = true
}

# Resources

resource "aws_kms_key" "backend_kms_key" {
  description = "KMS key for backend service on ${var.env} environment"
}

resource "aws_kms_alias" "backend_kms_key_alias" {
  name          = "alias/${local.service_name}-key"
  target_key_id = aws_kms_key.backend_kms_key.id
}

resource "aws_ssm_parameter" "sentry_dsn" {
  name   = "${local.service_name}-sentry-dsn"
  type   = "SecureString"
  value  = var.sentry_dsn
  key_id = aws_kms_key.backend_kms_key.arn
}

resource "aws_ssm_parameter" "db_password" {
  name   = "${local.service_name}-db-password"
  type   = "SecureString"
  value  = var.db_password
  key_id = aws_kms_key.backend_kms_key.arn
}

# Output

output "backend_kms_key_arn" {
  value = aws_kms_key.backend_kms_key.arn
}

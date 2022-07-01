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
  project_name          = "the-spymaster-backend"
  service_name          = "${local.project_name}-${var.env}"
  handler_function_name = local.service_name
  aws_account_id        = data.aws_caller_identity.current.account_id
  kms_env_map           = {
    "dev" : "arn:aws:kms:us-east-1:096386908883:key/59b86867-2b0d-4d48-bdee-87bdbf1e249a",
  }
  kms_arn                 = local.kms_env_map[var.env]
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

# Role

data "aws_iam_policy_document" "lambda_assume_policy_doc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com", "events.amazonaws.com", "apigateway.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name               = "${local.service_name}-exec-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_policy_doc.json
  inline_policy {
    name   = "${local.service_name}-exec-policy"
    policy = jsonencode(
      {
        "Version" : "2012-10-17",
        "Statement" : [
          {
            "Effect" : "Allow",
            "Action" : [
              "logs:CreateLogGroup",
              "logs:CreateLogStream",
              "logs:PutLogEvents"
            ],
            "Resource" : "arn:aws:logs:*:*:*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "ssm:GetParameter",
              "ssm:GetParameters",
            ],
            "Resource" : "arn:aws:ssm:${var.aws_region}:${local.aws_account_id}:parameter/${local.service_name}-*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "kms:Decrypt",
            ],
            "Resource" : local.kms_arn
          }
        ]
      }
    )
  }
  inline_policy {
    name   = "${local.service_name}-zappa-policy"
    policy = jsonencode(
      {
        "Version" : "2012-10-17",
        "Statement" : [
          {
            "Effect" : "Allow",
            "Action" : [
              "logs:*"
            ],
            "Resource" : "arn:aws:logs:*:*:*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "lambda:InvokeFunction"
            ],
            "Resource" : [
              "*"
            ]
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "xray:PutTraceSegments",
              "xray:PutTelemetryRecords"
            ],
            "Resource" : [
              "*"
            ]
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "ec2:AttachNetworkInterface",
              "ec2:CreateNetworkInterface",
              "ec2:DeleteNetworkInterface",
              "ec2:DescribeInstances",
              "ec2:DescribeNetworkInterfaces",
              "ec2:DetachNetworkInterface",
              "ec2:ModifyNetworkInterfaceAttribute",
              "ec2:ResetNetworkInterfaceAttribute"
            ],
            "Resource" : "*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "s3:*"
            ],
            "Resource" : "arn:aws:s3:::*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "kinesis:*"
            ],
            "Resource" : "arn:aws:kinesis:*:*:*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "sns:*"
            ],
            "Resource" : "arn:aws:sns:*:*:*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "sqs:*"
            ],
            "Resource" : "arn:aws:sqs:*:*:*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "dynamodb:*"
            ],
            "Resource" : "arn:aws:dynamodb:*:*:*"
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "route53:*"
            ],
            "Resource" : "*"
          }
        ]
      })
  }
}

# Outputs

output "execution_role_arn" {
  value = aws_iam_role.lambda_exec_role.arn
}

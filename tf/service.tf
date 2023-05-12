# Layer

module "layer_excludes" {
  source = "./python_excludes"
  path   = local.layer_src_root
}

data "archive_file" "layer_code_archive" {
  type        = "zip"
  source_dir  = local.layer_src_root
  output_path = "layer.zip"
  excludes    = module.layer_excludes.file_names
}

resource "aws_lambda_layer_version" "dependencies_layer" {
  filename         = data.archive_file.layer_code_archive.output_path
  layer_name       = "${local.service_name}-layer"
  source_code_hash = filebase64sha256(data.archive_file.layer_code_archive.output_path)
  skip_destroy     = true
}

# Lambda

module "lambda_excludes" {
  source = "./python_excludes"
  path   = local.lambda_src_root
}

data "archive_file" "service_code_archive" {
  type        = "zip"
  source_dir  = local.lambda_src_root
  output_path = "service.zip"
  excludes    = module.lambda_excludes.file_names
}

resource "aws_lambda_function" "service_lambda" {
  function_name                  = "${local.service_name}-lambda"
  role                           = aws_iam_role.lambda_exec_role.arn
  handler                        = "lambda_handler.handler"
  runtime                        = "python3.10"
  filename                       = data.archive_file.service_code_archive.output_path
  source_code_hash               = filebase64sha256(data.archive_file.service_code_archive.output_path)
  timeout                        = 15
  memory_size                    = 200
  reserved_concurrent_executions = 2
  layers                         = [
    aws_lambda_layer_version.dependencies_layer.arn
  ]
  environment {
    variables = {
      ENV_FOR_DYNACONF = local.env
    }
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
            "Resource" : local.default_key_arn
          },
          {
            "Effect" : "Allow",
            "Action" : [
              "dynamodb:DescribeTable",
              "dynamodb:GetItem",
              "dynamodb:PutItem",
            ],
            "Resource" : aws_dynamodb_table.games_items.arn
          }
        ]
      }
    )
  }
}

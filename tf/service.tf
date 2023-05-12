# Layer

resource "null_resource" "layer_code" {
  triggers = {
    requirements_hash = local.requirements_hash
  }
  provisioner "local-exec" {
    command = <<EOF
image_name="public.ecr.aws/sam/build-python3.10"
export_folder="${local.layer_relative}/python"
update_pip_cmd="pip install --upgrade pip"
install_dependencies_cmd="pip install -r requirements.lock -t $export_folder"
docker_cmd="$update_pip_cmd; $install_dependencies_cmd; exit"

cd ../; make export
docker run -v "${local.project_root}":/var/task "$image_name" /bin/sh -c "$docker_cmd"
EOF
  }
}

module "layer_archive" {
  source     = "git@github.com:asaf-kali/resources//tf/filtered_archive"
  source_dir = local.layer_src_root
  name       = "layer"
  depends_on = [null_resource.layer_code]
}

resource "aws_lambda_layer_version" "dependencies_layer" {
  layer_name       = "${local.service_name}-layer"
  filename         = module.layer_archive.output_path
  source_code_hash = filebase64sha256(module.layer_archive.output_path)
  skip_destroy     = true
  depends_on       = [
    module.layer_archive,
  ]
}

# Lambda

module "lambda_archive" {
  source     = "git@github.com:asaf-kali/resources//tf/filtered_archive"
  source_dir = local.lambda_src_root
  name       = "service"
}

resource "aws_lambda_function" "service_lambda" {
  function_name                  = "${local.service_name}-lambda"
  role                           = aws_iam_role.lambda_exec_role.arn
  handler                        = "lambda_handler.handler"
  runtime                        = "python3.10"
  filename                       = module.lambda_archive.output_path
  source_code_hash               = filebase64sha256(module.lambda_archive.output_path)
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
  depends_on = [
    module.lambda_archive,
  ]
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

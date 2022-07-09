# Lambda

#resource "aws_lambda_function" "handler_lambda" {
#  function_name                  = "${local.service_name}-lambda"
#  timeout                        = 15
#  role                           = aws_iam_role.lambda_exec_role.arn
#  image_uri                      = "${aws_ecr_repository.ecr_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
#  package_type                   = "Image"
#  memory_size                    = 200
#  reserved_concurrent_executions = 3
#
#  ephemeral_storage {
#    size = 10000
#  }
#
#  environment {
#    variables = {
#      ENV_FOR_DYNACONF = var.env
#    }
#  }
#  depends_on = [
#    null_resource.ecr_image
#  ]
#}

# Role

#data "aws_iam_policy_document" "lambda_assume_policy_doc" {
#  statement {
#    actions = ["sts:AssumeRole"]
#
#    principals {
#      type        = "Service"
#      identifiers = ["lambda.amazonaws.com", "events.amazonaws.com", "apigateway.amazonaws.com"]
#    }
#  }
#}
#
#resource "aws_iam_role" "lambda_exec_role" {
#  name               = "${local.service_name}-exec-role"
#  assume_role_policy = data.aws_iam_policy_document.lambda_assume_policy_doc.json
#  inline_policy {
#    name   = "${local.service_name}-exec-policy"
#    policy = jsonencode(
#      {
#        "Version" : "2012-10-17",
#        "Statement" : [
#          {
#            "Effect" : "Allow",
#            "Action" : [
#              "logs:CreateLogGroup",
#              "logs:CreateLogStream",
#              "logs:PutLogEvents"
#            ],
#            "Resource" : "arn:aws:logs:*:*:*"
#          },
#          {
#            "Effect" : "Allow",
#            "Action" : [
#              "ssm:GetParameter",
#              "ssm:GetParameters",
#            ],
#            "Resource" : "arn:aws:ssm:${var.aws_region}:${local.aws_account_id}:parameter/${local.service_name}-*"
#          },
#          {
#            "Effect" : "Allow",
#            "Action" : [
#              "kms:Decrypt",
#            ],
#            "Resource" : local.kms_arn
#          }
#        ]
#      }
#    )
#  }
#}

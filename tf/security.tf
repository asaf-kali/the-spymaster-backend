resource "aws_kms_key" "kms_key" {
  description = "KMS key for backend service."
}

resource "aws_kms_alias" "kms_key_alias" {
  name          = "alias/${local.service_name}-key"
  target_key_id = aws_kms_key.kms_key.id
}

resource "aws_ssm_parameter" "sentry_dsn" {
  name   = "${local.service_name}-sentry-dsn"
  type   = "SecureString"
  value  = var.sentry_dsn
  key_id = aws_kms_key.kms_key.arn
}

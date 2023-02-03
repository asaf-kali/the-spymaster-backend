#resource "aws_kms_key" "kms_key" {
#  description = "KMS key for backend service."
#}
#
#resource "aws_kms_alias" "kms_key_alias" {
#  name          = "alias/${local.service_name}-key"
#  target_key_id = aws_kms_key.kms_key.id
#}

resource "aws_ssm_parameter" "sentry_dsn" {
  name   = "${local.service_name}-sentry-dsn"
  type   = "SecureString"
  value  = var.sentry_dsn
  key_id = local.default_key_arn
}

resource "random_password" "django_secret_key" {
  length           = 64
  special          = true
  override_special = "_!%^"
}

resource "aws_ssm_parameter" "django_secret_key" {
  name  = "${local.service_name}-django-secret-key"
  type  = "SecureString"
  value = random_password.django_secret_key.result
}

# Password

resource "random_password" "admin_password" {
  length           = 24
  special          = true
  override_special = "_!%^"
}

resource "aws_ssm_parameter" "admin_password" {
  name   = "${local.service_name}-db-password"
  type   = "SecureString"
  value  = random_password.admin_password.result
  key_id = local.kms_arn
}

# RDS

resource "aws_db_instance" "service_db" {
  identifier          = "${local.service_name}-db"
  instance_class      = "db.t3.micro"
  engine              = "postgres"
  db_name             = "postgres"
  allocated_storage   = 10
  username            = "spymaster_admin"
  password            = aws_ssm_parameter.admin_password.value
  publicly_accessible = true
  skip_final_snapshot = true
}

output "db_hostname" {
  value = aws_db_instance.service_db.address
}

output "db_port" {
  value = aws_db_instance.service_db.port
}

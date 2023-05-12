variable "path" {
  type = string
}

locals {
  file_names = setunion(
    fileset(var.path, "**/__pycache__/**"),
    fileset(var.path, "**/*.pyc"),
  )
}

output "file_names" {
  value = local.file_names
}

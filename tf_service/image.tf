# Image

data "archive_file" "src_archive" {
  type        = "zip"
  source_dir  = "${local.project_root}/src"
  output_path = "source.zip"
}

resource "aws_ecr_repository" "ecr_repo" {
  name = "${local.service_name}-ecr"
}

resource "null_resource" "image_resource" {
  triggers = {
    docker_file = md5(file("${local.project_root}/Dockerfile"))
    source_dir  = data.archive_file.src_archive.output_sha
  }

  provisioner "local-exec" {
    command = <<EOF
           aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${local.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
           cd ${local.project_root}
           docker build -t ${aws_ecr_repository.ecr_repo.repository_url}:${local.ecr_image_tag} .
           docker push ${aws_ecr_repository.ecr_repo.repository_url}:${local.ecr_image_tag}
       EOF
  }
}

data "aws_ecr_image" "ecr_image" {
  repository_name = aws_ecr_repository.ecr_repo.name
  image_tag       = local.ecr_image_tag
  depends_on      = [
    null_resource.image_resource
  ]
}

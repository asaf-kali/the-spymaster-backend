#!/bin/bash
image_name="public.ecr.aws/sam/build-python3.9"
export_folder=".deployment/layer-dependencies/python"
update_pip_cmd="pip install --upgrade pip"
install_dependencies_cmd="pip install -r requirements.lock -t ${export_folder}"
docker_cmd="${update_pip_cmd}; ${install_dependencies_cmd}; exit"

sudo rm -rf "$export_folder"
poetry export --without-hashes -f requirements.txt --output requirements.lock --only main
docker run -v "$PWD":/var/task "$image_name" /bin/sh -c "$docker_cmd"

TERRAFORM_PLAN_FILE=deploy.tfplan
WORKSPACE=default

build-layer:
	cd ../; make build-layer

plan:
	terraform workspace select $(WORKSPACE)
	terraform plan -out $(TERRAFORM_PLAN_FILE) -var-file="$(WORKSPACE).tfvars"

apply:
	terraform apply $(TERRAFORM_PLAN_FILE)

deploy: build-layer plan apply

update:
	terraform get -update

SHELL := /bin/bash

.PHONY: help init plan apply destroy

help:
	@echo "Alpine Lambda Trade (ALT) - Commands"
	@echo "  make init      : Initialize Terraform"
	@echo "  make plan      : Plan Terraform infrastructure"
	@echo "  make apply     : Apply Terraform infrastructure"
	@echo "  make destroy   : Destroy Terraform infrastructure"

init:
	cd infra && \
	set -a && source ../.env && set +a && \
	terraform init

plan:
	cd infra && \
	set -a && source ../.env && set +a && \
	terraform plan

apply:
	cd infra && \
	set -a && source ../.env && set +a && \
	terraform apply

destroy:
	cd infra && \
	set -a && source ../.env && set +a && \
	terraform destroy

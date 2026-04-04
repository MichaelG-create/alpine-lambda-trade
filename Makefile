SHELL := /bin/bash

.PHONY: help init plan apply destroy

help:
	@echo "Alpine Lambda Trade (ALT) - Commands"
	@echo "  make init      : Initialize Terraform"
	@echo "  make plan      : Plan Terraform infrastructure"
	@echo "  make apply     : Apply Terraform infrastructure"
	@echo "  make destroy   : Destroy Terraform infrastructure"
	@echo "  make local-infra-up : Start LocalStack for local testing"
	@echo "  make local-infra-down : Stop LocalStack"
	@echo "  make run-producer   : Run the producer script (dev)"
	@echo "  make test-producer  : Run the tests for the producer"

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

local-infra-up:
	docker compose up -d localstack

local-infra-down:
	docker compose down

run-producer:
	set -a && source .env && set +a && \
	export PYTHONPATH=. && \
	uv run python src/producer/main.py

test-producer:
	set -a && source .env && set +a && \
	export PYTHONPATH=. && \
	uv run pytest tests/producer/ -v --cov=src/producer

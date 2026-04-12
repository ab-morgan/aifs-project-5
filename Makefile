# CareerPivots — Makefile
# Usage:
#   make dev       Start the app in development mode (port 8300, debug logging)
#   make prod      Start the app in production mode (port 8501, errors only)
#   make prep      Run the embedding prep pipeline
#   make test      Run the test suite
#   make lint      Run ruff linter
#   make help      Show this help

.DEFAULT_GOAL := help

# ── Environment ────────────────────────────────────────────────────────────

SHELL := /bin/bash
PYTHON := python

# ── Targets ────────────────────────────────────────────────────────────────

.PHONY: dev
dev: ## Start the app in development mode (APP_ENV=dev, port 8300)
	@APP_ENV=dev bash version2/run_app.sh

.PHONY: prod
prod: ## Start the app in production mode (APP_ENV=prod, port 8501)
	@APP_ENV=prod bash version2/run_app.sh

.PHONY: prep
prep: ## Run the embedding + stats prep pipeline
	@echo ""
	@echo "  Running prep pipeline..."
	@echo ""
	@cd version2 && APP_ENV=$${APP_ENV:-dev} $(PYTHON) -m prep.prep_runner

.PHONY: test
test: ## Run the test suite (single pass, no watch mode)
	@echo ""
	@echo "  Running tests..."
	@echo ""
	@APP_ENV=dev $(PYTHON) -m pytest version2/tests/ -ra -q

.PHONY: lint
lint: ## Run ruff linter over version2/
	@$(PYTHON) -m ruff check version2/

.PHONY: help
help: ## Show available targets
	@echo ""
	@echo "  CareerPivots — available make targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-10s\033[0m %s\n", $$1, $$2}'
	@echo ""

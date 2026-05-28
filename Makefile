# CareerPivots — Makefile
#
# Intended workflow:
#   1. make prep          — run ONCE before starting the app (or after job data changes)
#   2. make dev / prod    — start the app; it reads from the precomputed data in Supabase
#
# The prep step computes embeddings and statistics and stores them in Supabase.
# The app loads that data into a process-level cache on first startup and serves
# all users from cache — Supabase is not queried again until the process restarts.

.DEFAULT_GOAL := help

SHELL  := /bin/bash
PYTHON := python

# ── Prep ───────────────────────────────────────────────────────────────────

.PHONY: prep-dev
prep-dev: ## [STEP 1 — dev] Run prep against dev Supabase (small batches, verbose)
	@APP_ENV=dev bash version2/run_prep.sh

.PHONY: prep-prod
prep-prod: ## [STEP 1 — prod] Run prep against prod Supabase (full batches, errors only)
	@APP_ENV=prod bash version2/run_prep.sh

.PHONY: prep
prep: prep-dev ## Alias for prep-dev (default environment)

.PHONY: prep-dev-force
prep-dev-force: ## Re-compute ALL dev embeddings + stats even if they already exist
	@APP_ENV=dev bash version2/run_prep.sh --force

.PHONY: prep-prod-force
prep-prod-force: ## Re-compute ALL prod embeddings + stats even if they already exist
	@APP_ENV=prod bash version2/run_prep.sh --force

# ── App ────────────────────────────────────────────────────────────────────

.PHONY: dev
dev: ## [STEP 2] Start the app in development mode (port 8300, debug logging)
	@APP_ENV=dev bash version2/run_app.sh

.PHONY: prod
prod: ## [STEP 2] Start the app in production mode (port 8501, errors only)
	@APP_ENV=prod bash version2/run_app.sh

# ── Quality ────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run the full test suite (no live services needed — all mocked)
	@echo ""
	@echo "  Running tests (APP_ENV=dev, all external services mocked)..."
	@echo ""
	@APP_ENV=dev $(PYTHON) -m pytest version2/tests/ -ra -q

.PHONY: test-prep
test-prep: ## Run only the prep pipeline tests
	@APP_ENV=dev $(PYTHON) -m pytest version2/tests/test_prep_pipeline.py -v

.PHONY: lint
lint: ## Run ruff linter over version2/
	@$(PYTHON) -m ruff check version2/

# ── Help ───────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show available targets
	@echo ""
	@echo "  CareerPivots — make targets"
	@echo ""
	@echo "  Typical startup sequence:"
	@echo "    make prep-dev    # populate dev Supabase with embeddings + stats"
	@echo "    make dev         # start the app in dev mode"
	@echo ""
	@echo "    make prep-prod   # populate prod Supabase with embeddings + stats"
	@echo "    make prod        # start the app in prod mode"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""

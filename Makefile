.PHONY: help sync install test build wheel docs docs-clean clean distclean

UV := uv
SPHINXBUILD := sphinx-build
DOCS_SOURCE := docs/source
DOCS_BUILD := docs/build/html

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@printf "  \033[36m%-15s\033[0m %s\n" "help" "Show this help message"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| grep -v '^help:' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

sync: ## Sync the uv environment
	$(UV) sync

install: sync ## Alias for sync

test: ## Run the test suite with pytest
	$(UV) run pytest

build: ## Build source distribution and wheel
	$(UV) build

wheel: ## Build only a wheel
	$(UV) build --wheel

docs: ## Build the Sphinx documentation
	$(UV) run --with-requirements docs/requirements.txt $(SPHINXBUILD) -b html -E $(DOCS_SOURCE) $(DOCS_BUILD)

docs-clean: ## Remove generated documentation
	rm -rf docs/build

clean: ## Remove common build/test artifacts
	rm -rf build dist .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +

distclean: clean docs-clean ## Remove all generated artifacts
	rm -rf *.egg-info src/*.egg-info

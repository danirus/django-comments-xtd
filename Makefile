.DEFAULT_GOAL := help

.PHONY: coverage help

clean:  ## Remove build files.
	rm -rf dist
	rm -rf docs/_build/
	rm -rf docs/__pycache__/
	rm -rf django_comments_xtd/static/django_comments_xtd/js/coverage
	rm -rf django_comments_xtd/static/django_comments_xtd/js/django-comments-xtd-*.js*

lint:  ## Run pre-commit hook checks.
	pre-commit run --all-files --show-diff-on-failure

py-tests:  ## Run Python tests with coverage.
	coverage erase
	coverage run --source=django_comments_xtd -m pytest -ra
	coverage report -m

js-tests:  ## Run JavaScript tests.
	npm run test

build:  clean  ## Build django-comments-xtd package.
	npm run css
	npm run js
	python -m build

help: ## Show help message.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

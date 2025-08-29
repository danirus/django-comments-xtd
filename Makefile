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

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done

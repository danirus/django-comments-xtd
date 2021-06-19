.DEFAULT_GOAL := help
.PHONY: coverage deps help lint test tox

coverage:  ## Run tests with coverage.
	coverage erase
	coverage run --include=django_comments_xtd/* \
				 --omit=django_comments_xtd/migrations/* -m pytest -ra
	coverage report -m

deps:  ## Install dependencies.
	pip install coverage flake8 pylint pytest pytest-django tox
	pip install -r requirements.txt

pep8:  ## Check PEP8 compliance.
	flake8 django_comments_xtd

lint:  ## Run pylint.
	pylint django_comments_xtd

test:  ## Run tests.
	py.test

tox:  ## Run tox.
	python -m tox

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

	.DEFAULT_GOAL := help
.PHONY: coverage deps help tox sdist collectstatic \
	compose-project-quotes-build compose-project-quotes-up

coverage:  ## Run tests with coverage.
	coverage erase
	coverage run --source=django_comments_xtd \
		--omit=*migrations*,*tests* -m pytest -ra
	coverage report -m

deps:  ## Install dependencies.
	pip install coverage flake8 pylint pytest pytest-django tox
	pip install -r requirements.txt

pep8:  ## Check PEP8 compliance.
	flake8 --exclude=.tox,docs,django_comments_xtd/tests,django_comments_xtd/__init__.py,django_comments_xtd/migrations --max-line-length=80 --extend-ignore=E203 django_comments_xtd

tox:  ## Run tox.
	python -m tox

sdist:  # Create source tarballs for django-comments-xtd and demos projects.
	python setup.py sdist
	cd demos/project-quotes/ && python setup.py sdist

collectstatic:  # django's collectstatic for demos project.
	cd demos/project-quotes/ && . pqenv/bin/activate && python project_quotes/manage.py collectstatic --noinput

compose-project-quotes-build: sdist
	source .env && docker-compose -f demos/project-quotes/docker-compose.yml build web

compose-project-quotes-up: sdist collectstatic
	source .env && docker-compose -f demos/project-quotes/docker-compose.yml up

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

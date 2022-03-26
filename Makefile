	.DEFAULT_GOAL := help
.PHONY: coverage deps pep8 check-syntax format-syntax help tox sdist \
	collectstatic compose-project-quotes-build compose-project-quotes-up

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

check-syntax:
	ufmt check django_comments_xtd/

format-syntax:
	ufmt format django_comments_xtd/

tox:  ## Run tox.
	python -m tox

sdist-project-quotes:  # Create source tarballs for django-comments-xtd and demos projects.
	. venv/bin/activate && python setup.py sdist && deactivate
	cd demos/project-quotes/ && . pqenv/bin/activate && python setup.py sdist && deactivate

collectstatic-project-quotes:  # django's collectstatic for demos project.
	cd demos/project-quotes/ && . pqenv/bin/activate && python project_quotes/manage.py collectstatic --noinput && deactivate

compose-project-quotes-build: sdist-project-quotes
	source .env && docker-compose -f demos/project-quotes/docker-compose.yml build web

compose-project-quotes-up: sdist-project-quotes collectstatic-project-quotes
	source .env && docker-compose -f demos/project-quotes/docker-compose.yml up -d

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

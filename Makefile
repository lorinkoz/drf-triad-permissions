# Makefile for drf-triad-permissions

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: test
test:
	poetry run triads_sandbox/manage.py test tests

.PHONY: coverage
coverage:
	poetry run coverage run triads_sandbox/manage.py test tests

.PHONY: coverage-html
coverage-html:
	poetry run coverage run triads_sandbox/manage.py test tests && poetry run coverage html

.PHONY: reqs
reqs:
	poetry export --without-hashes --dev --format requirements.txt > requirements.txt

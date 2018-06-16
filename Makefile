.PHONY: all
all: install

.PHONY: install
install: .venv/flag
.venv/flag: pyproject.lock
	@ poetry config settings.virtualenvs.in-project true
	poetry develop
	@ touch $@

pyproject.lock: pyproject.toml
	poetry lock

###############################################################################

.PHONY: ci
ci: format check test

.PHONY: format
format: install
	poetry run isort form tests --recursive --apply
	poetry run black form tests --line-length=79 --py36

.PHONY: check
check: install

.PHONY: test
test: install
	poetry run pytest

.PHONY: watch
watch: install
	poetry run rerun "make test format check" -i .coverage -i htmlcov

###############################################################################

.PHONY: clean
clean:
	rm -rf .venv

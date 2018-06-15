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
ci: check test

.PHONY: check
check: install
	poetry run isort yorm2 tests --recursive --apply
	poetry run black yorm2 tests --line-length=79 --py36

.PHONY: test
test: install
	poetry run pytest

###############################################################################

.PHONY: clean
clean:
	rm -rf .venv

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
	poetry run rerun "make test check" --ignore=.coverage; make format

###############################################################################

.PHONY: clean
clean:
	rm -rf .venv

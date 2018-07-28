.PHONY: all
all: install

###############################################################################

VIRTUAL_ENV ?= .venv

.PHONY: install
install: $(VIRTUAL_ENV)/flag
$(VIRTUAL_ENV)/flag: pyproject.lock
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
	poetry run black form tests --line-length=79 --py36 --skip-string-normalization

.PHONY: check
check: install

.PHONY: test
test: install
	@ mkdir -p .cache
	poetry run pytest --disable-warnings

.PHONY: watch
watch: install
	poetry run ptw

###############################################################################

.PHONY: clean
clean:
	rm -rf .venv

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

PACKAGES :=  datafiles tests

BLACK_OPTIONS := --line-length=79 --py36 --skip-string-normalization

.PHONY: ci
ci: format check test

.PHONY: check
check: install
	poetry run isort $(PACKAGES) --recursive --apply
	poetry run black $(PACKAGES) $(BLACK_OPTIONS)
ifdef CI
	git diff --exit-code
endif
	poetry run pylint $(PACKAGES) --rcfile=.pylint.ini
	poetry run mypy $(PACKAGES) --config-file=.mypy.ini

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

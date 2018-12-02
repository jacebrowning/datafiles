.PHONY: all
all: install

###############################################################################

VIRTUAL_ENV ?= .venv

.PHONY: install
install: $(VIRTUAL_ENV)/flag .cache
$(VIRTUAL_ENV)/flag: pyproject.lock
	@ poetry config settings.virtualenvs.in-project true
	poetry install
	@ touch $@

pyproject.lock: pyproject.toml
	poetry lock
	@ touch $@

.cache:
	@ mkdir -p .cache

###############################################################################

PACKAGES :=  datafiles tests

.PHONY: ci
ci: format check test

.PHONY: format
format: install
	poetry run isort $(PACKAGES) --recursive --apply
	poetry run black $(PACKAGES)
	@ echo

.PHONY: check
check: install format
ifdef CI
	git diff --exit-code
endif
	poetry run pylint $(PACKAGES) --rcfile=.pylint.ini
	poetry run mypy $(PACKAGES) --config-file=.mypy.ini

.PHONY: test
test: install
	poetry run pytest --random $(PYTEST_OPTIONS)
	poetry run coveragespace jacebrowning/datafiles overall

.PHONY: watch
watch: install
	poetry run ptw

###############################################################################

.PHONY: demo
demo: install
	poetry run jupyter notebook --notebook-dir=notebooks

###############################################################################

.PHONY: clean
clean:
	rm -rf .venv

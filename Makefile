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

.PHONY: format
format: install
	poetry run isort $(PACKAGES) --recursive --apply
	poetry run black $(PACKAGES) $(BLACK_OPTIONS)

.PHONY: check
check: install format
ifdef CI
	git diff --exit-code
endif
	poetry run pylint $(PACKAGES) --rcfile=.pylint.ini
	poetry run mypy $(PACKAGES) --config-file=.mypy.ini

.PHONY: test
test: install
	@ mkdir -p .cache
	poetry run pytest
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

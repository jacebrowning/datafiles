.PHONY: all
all: install

.PHONY: ci
ci: format check test

# SYSTEM DEPENDENCIES #########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	@ pip install --user verchew > /dev/null
	verchew

# PROJECT DEPENDENCIES ########################################################

VIRTUAL_ENV ?= .venv

.PHONY: install
install: $(VIRTUAL_ENV)/flag .cache
$(VIRTUAL_ENV)/flag: poetry.lock
	@ poetry config settings.virtualenvs.in-project true
	poetry install
	@ touch $@

poetry.lock: pyproject.toml
	poetry lock
	@ touch $@

.cache:
	@ mkdir -p .cache

# VALIDATION TARGETS ##########################################################

PACKAGES :=  datafiles tests

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
	poetry run pytest --random
	poetry run coveragespace jacebrowning/datafiles overall

.PHONY: test-repeat
test-repeat: install
	poetry run pytest --count=5 --random --exitfirst

.PHONY: watch
watch: install
	poetry run ptw

# DEMO ########################################################################

.PHONY: demo
demo: install
	poetry run jupyter notebook --notebook-dir=notebooks

# CLEANUP #####################################################################

.PHONY: clean
clean:
	rm -rf .venv

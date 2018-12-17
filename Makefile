# Project settings
PROJECT := Datafiles
PACKAGE := datafiles
REPOSITORY := jacebrowning/datafiles

# Project paths
PACKAGES := $(PACKAGE) tests
MODULES := $(wildcard $(PACKAGE)/*.py)

.PHONY: all
all: install

.PHONY: ci
ci: format check test docs

# SYSTEM DEPENDENCIES #########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	bin/verchew

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

# DOCUMENTATION ###############################################################

PYREVERSE := poetry run pyreverse
MKDOCS := poetry run mkdocs

MKDOCS_INDEX := site/index.html

.PHONY: docs
docs: uml mkdocs ## Generate documentation

.PHONY: uml
uml: install docs/*.png
docs/*.png: $(MODULES)
	$(PYREVERSE) $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	- mv -f classes_$(PACKAGE).png docs/classes.png
	- mv -f packages_$(PACKAGE).png docs/packages.png

.PHONY: mkdocs
mkdocs: install $(MKDOCS_INDEX)
$(MKDOCS_INDEX): mkdocs.yml docs/*.md
	mkdir -p docs/about
	cd docs && ln -sf ../README.md index.md
	cd docs/about && ln -sf ../../CHANGELOG.md changelog.md
	cd docs/about && ln -sf ../../CONTRIBUTING.md contributing.md
	cd docs/about && ln -sf ../../LICENSE.md license.md
	$(MKDOCS) build --clean --strict

.PHONY: mkdocs-live
mkdocs-live: mkdocs
	eval "sleep 3; bin/open http://127.0.0.1:8000" &
	$(MKDOCS) serve

# DEMO ########################################################################

.PHONY: demo
demo: install
	poetry run jupyter notebook --notebook-dir=notebooks

# CLEANUP #####################################################################

.PHONY: clean
clean:
	rm -rf .venv

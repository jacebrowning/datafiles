PACKAGE := datafiles
MODULES := $(wildcard $(PACKAGE)/*.py)

# MAIN TASKS ##################################################################

.PHONY: all
all: doctor format check test mkdocs ## Run all tasks that determine CI status

.PHONY: dev
dev: install  ## Continuously run all CI tasks when files chanage
	poetry run ptw

.PHONY: shell
shell: install
	poetry run ipython --ipython-dir=notebooks

.PHONY: demo
demo: install
	poetry run nbstripout notebooks/*.ipynb
	poetry run jupyter notebook --notebook-dir=notebooks --browser=firefox

# SYSTEM DEPENDENCIES #########################################################

.PHONY: bootstrap
bootstrap: ## Attempt to install system dependencies
	asdf plugin add python || asdf plugin update python
	asdf plugin add poetry https://github.com/asdf-community/asdf-poetry.git || asdf plugin update poetry
	asdf install

.PHONY: doctor
doctor: ## Confirm system dependencies are available
	bin/verchew

# PROJECT DEPENDENCIES ########################################################

VIRTUAL_ENV ?= .venv
DEPENDENCIES := $(VIRTUAL_ENV)/.poetry-$(shell bin/checksum pyproject.toml poetry.lock)

.PHONY: install
install: $(DEPENDENCIES) .cache ## Install project dependencies

$(DEPENDENCIES): poetry.lock
	@ rm -rf $(VIRTUAL_ENV)/.poetry-*
	@ poetry config virtualenvs.in-project true
	poetry install
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock --no-update
	@ touch $@
endif

.cache:
	@ mkdir -p .cache

# CHECKS ######################################################################

.PHONY: format
format: install
	poetry run isort $(PACKAGE) tests
	poetry run black $(PACKAGE) tests
	@ echo

.PHONY: check
check: install format  ## Run formaters, linters, and static analysis
ifdef CI
	git diff --exit-code
endif
	poetry run mypy $(PACKAGE) tests --config-file=.mypy.ini
	poetry run pylint $(PACKAGE) tests --rcfile=.pylint.ini
	poetry run pydocstyle $(PACKAGE) tests

# TESTS #######################################################################

.PHONY: test
test: install  ## Run unit and integration tests
	poetry run pytest --random
	poetry run coveragespace update overall

.PHONY: test-repeat
test-repeat: install
	poetry run pytest --count=5 --random --exitfirst --cov-report=xml

.PHONY: test-profile
test-profile: install
	poetry run pytest tests/test_profiling.py --profile-svg

# DOCUMENTATION ###############################################################

MKDOCS_INDEX := site/index.html

.PHONY: docs
docs: mkdocs uml notebooks  ## Generate documentation and UML

.PHONY: mkdocs
mkdocs: install $(MKDOCS_INDEX)
$(MKDOCS_INDEX): docs/requirements.txt mkdocs.yml docs/*.md
	@ mkdir -p docs/about
	@ cd docs/about && ln -sf ../../CHANGELOG.md changelog.md
	@ cd docs/about && ln -sf ../../CONTRIBUTING.md contributing.md
	@ cd docs/about && ln -sf ../../LICENSE.md license.md
	poetry run mkdocs build --clean --strict

docs/requirements.txt: poetry.lock
	@ rm -f $@
	@ poetry export --with dev --without-hashes | grep jinja2 >> $@
	@ poetry export --with dev --without-hashes | grep markdown >> $@
	@ poetry export --with dev --without-hashes | grep mkdocs >> $@
	@ poetry export --with dev --without-hashes | grep pygments >> $@
	@ poetry export --with dev --without-hashes | grep importlib-metadata >> $@

.PHONY: mkdocs-serve
mkdocs-serve: mkdocs
	eval "sleep 3; bin/open http://127.0.0.1:8000" &
	poetry run mkdocs serve

.PHONY: uml
uml: install docs/*.png
docs/*.png: $(MODULES)
	poetry run pyreverse $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	- mv -f classes_$(PACKAGE).png docs/classes.png
	- mv -f packages_$(PACKAGE).png docs/packages.png

.PHONY: notebooks
notebooks: install
	@ cd notebooks; for filename in *.ipynb; do \
	  poetry run papermill $$filename $$filename; \
	done
	git config filter.nbstripout.extrakeys 'cell.id cell.metadata.execution cell.metadata.papermill metadata.papermill'
	poetry run nbstripout --keep-output notebooks/*.ipynb

# RELEASE #####################################################################

DIST_FILES := dist/*.tar.gz dist/*.whl

.PHONY: dist
dist: install $(DIST_FILES)
$(DIST_FILES): $(MODULES) pyproject.toml
	rm -f $(DIST_FILES)
	poetry build

.PHONY: upload
upload: dist  ## Upload the current version to PyPI
	git diff --name-only --exit-code
	poetry publish
	bin/open https://pypi.org/project/$(PACKAGE)

# CLEANUP #####################################################################

.PHONY: clean
clean:  ## Delete all generated and temporary files
	rm -rf .venv

# HELP ########################################################################

.PHONY: help
help: install
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

# Release Notes

## 2.2.2 (2024-01-06)

- Fixed `Manager.all()` behavior for patterns with default vales.

## 2.2.1 (2024-01-04)

- Updated `Manager.get()` to handle default values in pattern arguments.

## 2.2 (2023-10-14)

- Added a `sync()` utility to map arbitrary objects to the filesystem.

## 2.1.2 (2023-05-27)

- Fixed the `mypy` plugin to support newer versions.

## 2.1.1 (2023-05-04)

- Fixed missing default value for `target_object` in container converters.

## 2.1 (2023-03-26)

- Added support for Python 3.11.
- Updated `Manager.get()` to be more flexible with positional arguments.
- Added support for passing `frozen=True` to the underlying `dataclass`.
- Added `py.typed` to tell type checkers that `datafiles` has types.

## 2.0 (2022-08-20)

- Dropped support for Python 3.7.

## 1.4.3 (2022-08-19)

- Fixed handling of invalid YAML files in manager methods.

## 1.4.2 (2022-07-29)

- Fixed exception when `Union[int, float]` or `Union[str, ...]` is used.

## 1.4.1 (2022-07-28)

- Fixed exception when `TypedDict` is used, but schema is not yet supported.

## 1.4 (2022-06-03)

- Added support for accessing `Dict` keys as attributes.
- Added a proper `repr()` implementation for `auto()` datafiles.
- Added support for "thawing" objects upon exiting the `frozen()` context manager.

## 1.3 (2022-04-09)

- Added support for paths relative to the user's home directory.

## 1.2 (2022-02-24)

- Added a `frozen()` context manager to temporarily disable file updates.

## 1.1.1 (2022-02-02)

- Fixed handling of `OSError` when trying to determine a models path.

## 1.1 (2022-01-21)

- Added support for Python 3.10's builtin optional types (e.g. `int | None`).
- Fixed handling of commented blocks in YAML files.
- Fixed serialization for `list` of `dict` in YAML.

## 1.0 (2021-10-04)

- Initial stable release.

## 0.15.2 (2021-09-03)

- Fixed `ValueError` when loading enum values from TOML files.

## 0.15.1 (2021-07-01)

- Fixed handling of no file extension to use YAML by default.

## 0.15 (2021-05-26)

- Removed `auto_load`/`auto_save` model options.
- Removed `INDENT_YAML_BLOCKS` setting.
- Removed `YAML_LIBRARY` setting.
- Renamed `HIDE_TRACEBACK_IN_HOOKS` setting to `HIDDEN_TRACEBACK`.
- Renamed `MINIMIZE_LIST_DIFFS` settings to `MINIMAL_DIFFS`.

## 0.14 (2021-05-21)

- Renamed model option `auto_attr` to `infer`.
- Deprecated `auto_load`/`auto_save` model options in favor of `manual`.

## 0.13.3 (2021-05-20)

- Added support for filtering on nested attributes.

## 0.13.2 (2021-05-16)

- Fixed loading of partially defined nested objects with optional attributes.

## 0.13.1 (2021-04-18)

- Fixed handling of string annotations for extended types.

## 0.13 (2021-04-17)

- Added support for generic types.
- Added support for sets.
- Updated default `attrs` to exclude computed properties, i.e. `field(init=False)`.
- Fixed automatic save when modifying nested dictionary values.
- Fixed initialization for non-compliant `None` default values.

## 0.12 (2021-03-05)

- Added `_exclude` parameter to `all()` and `filter()` manager methods to exclude certain objects from loading as a performance optimization.
- Fixed handling of untyped `List`/`Dict` annotations in Python 3.9.
- Fixed `ValueError` when setting an `Optional[<enum>]` to `None`.

## 0.11.1 (2020-09-12)

- Fixed error message for `Dict` annotations lacking types.

## 0.11 (2020-09-10)

- Added support to treat `Mapping` type annotations as dictionaries.
- Fixed handling of default values for `dataclass` attributes.
- Added `MINIMIZE_LIST_DIFFS` setting to control the semantic representation of empty lists.

## 0.10 (2020-07-03)

- Added support for recursively matching arbitrary depth paths of files.
- Fixed `AttributeError` when attempting to load malformed YAML files.

## 0.9 (2020-04-13)

- Fixed serialization of optional nested dataclasses with a value of `None`.
- Fixed preservation of comments on nested dataclass attributes.
- Added support for using `enum.Enum` subclasses as type annotations.

## 0.8.1 (2020-03-30)

- Fixed loading of `Missing` nested dataclasses attributes.

## 0.8 (2020-03-28)

- Updated the `@datafile(...)` decorator to be used as a drop-in replacement for `@dataclass(...)`.
- Added support for loading unlimited levels of nested objects.

## 0.7 (2020-02-20)

- Added a `YAML_LIBRARY` setting to control the underlying YAML library.
- Fixed ORM methods to handle relative file patterns.
- Updated the `@datafile` decorator to be able to be called without parentheses to act as `@dataclass`.
- Updated YAML serialization to preserve quotation marks in files.

## 0.6 (2020-01-25)

- Added a registration system for custom formatter classes.
- Fixed loading of missing attribute from disk for ORM methods.
- Added support for file patterns relative to the current directory.

## 0.5.1 (2019-11-14)

- Removed unnecessary warning when loading objects.

## 0.5 (2019-09-28)

- Added an `INDENT_YAML_BLOCKS` setting to optionally use the old serialization behavior.
- Disabled initial file creation when `settings.HOOKS_ENABLED = False` is set.

## 0.4.2 (2019-09-27)

- Fixed a `TypeError` when converting custom types with `from __future__ import annotations` enabled.

## 0.4.1 (2019-08-25)

- Fixed a `TypeError` when converting non-builtin attributes.

## 0.4 (2019-06-29)

- Fixed ORM methods for datafiles with relative path patterns.
- Added plugin for `mypy` support.
- Updated YAML format to indent lists.

## 0.3 (2019-06-09)

- Added ORM method: `all()`
- Added ORM method: `get_or_none()`.
- Added ORM method: `get_or_create()`.
- Added ORM method: `filter`.

## 0.2 (2019-03-30)

- Added an option to automatically resave files after loading.
- Added an option to automatically reload files after saving.
- Added a registration system for custom converter classes.
- Added initial support for file inference via `auto(filename)`.

## 0.1 (2019-01-13)

- Initial release.

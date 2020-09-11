# 0.11 (2020-09-10)

- Added support to treat `Mapping` type annotations as dictionaries.
- Fixed handling of default values for `dataclass` attributes.
- Added `MINIMIZE_LIST_DIFFS` setting to control the semantic representation of empty lists.

# 0.10 (2020-07-03)

- Added support for recursively matching arbitrary depth paths of files.
- Fixed `AttributeError` when attempting to load malformed YAML files.

# 0.9 (2020-04-13)

- Fixed serialization of optional nested dataclasses with a value of `None`.
- Fixed preservation of comments on nested dataclass attributes.
- Added support for using `enum.Enum` subclasses as type annotations.

# 0.8.1 (2020-03-30)

- Fixed loading of `Missing` nested dataclasses attributes.

# 0.8 (2020-03-28)

- Updated the `@datafile(...)` decorator to be used as a drop-in replacement for `@dataclass(...)`.
- Added support for loading unlimited levels of nested objects.

# 0.7 (2020-02-20)

- Added a `YAML_LIBRARY` setting to control the underlying YAML library.
- Fixed ORM methods to handle relative file patterns.
- Updated the `@datafile` decorator to be able to be called without parentheses to act as `@dataclass`.
- Updated YAML serialization to preserve quotation marks in files.

# 0.6 (2020-01-25)

- Added a registration system for custom formatter classes.
- Fixed loading of missing attribute from disk for ORM methods.
- Added support for file patterns relative to the current directory.

# 0.5.1 (2019-11-14)

- Removed unnecessary warning when loading objects.

# 0.5 (2019-09-28)

- Added an `INDENT_YAML_BLOCKS` setting to optionally use the old serialization behavior.
- Disabled initial file creation when `settings.HOOKS_ENABLED = False` is set.

# 0.4.2 (2019-09-27)

- Fixed a `TypeError` when converting custom types with `from __future__ import annotations` enabled.

# 0.4.1 (2019-08-25)

- Fixed a `TypeError` when converting non-builtin attributes.

# 0.4 (2019-06-29)

- Fixed ORM methods for datafiles with relative path patterns.
- Added plugin for `mypy` support.
- Updated YAML format to indent lists.

# 0.3 (2019-06-09)

- Added ORM method: `all()`
- Added ORM method: `get_or_none()`.
- Added ORM method: `get_or_create()`.
- Added ORM method: `filter`.

# 0.2 (2019-03-30)

- Added an option to automatically resave files after loading.
- Added an option to automatically reload files after saving.
- Added a registration system for custom converter classes.
- Added initial support for file inference via `auto(filename)`.

# 0.1 (2019-01-13)

- Initial release.

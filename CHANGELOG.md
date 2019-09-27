# 0.5 (unreleased)

- Added an `INDENT_YAML_BLOCKS` setting to optionally use the old serialization behavior.

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
- Added registration system for custom class converters.
- Added initial support for file inference via `auto(filename)`.

# 0.1 (2019-01-13)

 - Initial release.

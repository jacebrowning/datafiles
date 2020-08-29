<h1>Settings</h1>

For clients that wish to temporarily alter any of the previously described behaviors, a handful of settings can be controlled at the module level. All values default to `True` unless otherwise noted.

# `HIDE_TRACEBACK_IN_HOOKS`

When an exception occurs in patched method, this traceback is hidden by default for `pytest`. If this information is required to debug a complex issue enable it as follows:

```python
import datafiles

datafiles.settings.HIDE_TRACEBACK_IN_HOOKS = False
```

# `HOOKS_ENABLED`

When running unit tests for a client using `datafiles`,
it can be helpful to disable automatic loading/saving of models for performance and to avoid writing files to disk:

```python
import datafiles

def pytest_runtest_setup(item):
    """Disable file storage during unit tests."""
    datafiles.settings.HOOKS_ENABLED = False
```

# `INDENT_YAML_BLOCKS`

In `datafiles >= 0.4`, YAML blocks are now indented by default, like so:

```yaml
items:
  - 1
  - 2
  - 3
```

To make it easier to upgrade to this version, a client can disable this functionality:

```python
import datafiles

datafiles.settings.INDENT_YAML_BLOCKS = False
```

to produce YAML like:

```yaml
items:
- 4
- 5
- 6
```

# `MINIMIZE_LIST_DIFFS`

When serializing lists, `datafiles` intentionally deviates from the semantic representation of an empty list to optimize for the use case of storing YAML files in version control.

By storing any empty list of `items` as:

```yaml
items:
  -
```

adding or removing an item always results in a one-line change. Where as adding items to `items: []` produces a noisier diff and requires knowledge of the YAML specification to edit files by hand.

To disable this behavior:

```python
import datafiles

datafiles.settings.MINIMIZE_LIST_DIFFS = False
```

# `YAML_LIBRARY`

This setting controls the underlying YAML library used to read and write files. The following options are available:

- `'ruamel.yaml'` (default)
- `'PyYAML'`

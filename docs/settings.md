# Settings

For clients that wish to temporarily alter any of the previously described behaviors, a handful of settings can be controlled at the module level. All values default to `True` unless otherwise noted.

## `HIDDEN_TRACEBACK`

When an exception occurs in patched method, this traceback is hidden by default for `pytest`. If this information is required to debug a complex issue enable it as follows:

```python
import datafiles

datafiles.settings.HIDDEN_TRACEBACK = False
```

## `HOOKS_ENABLED`

When running unit tests for a client using `datafiles`,
it can be helpful to disable automatic loading/saving of models for performance and to avoid writing files to disk:

```python
import datafiles

def pytest_runtest_setup(item):
    """Disable file storage during unit tests."""
    datafiles.settings.HOOKS_ENABLED = False
```

## `MINIMAL_DIFFS`

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

datafiles.settings.MINIMAL_DIFFS = False
```

## `WRITE_DELAY`

One some file systems, the modification time of a file ([`st_mtime`](https://docs.python.org/3/library/os.html#os.stat_result.st_mtime)) is unchanged if a file is read immediately after writing. This may cause intermittent issues if your use case involves rapidly changing files.

To compensate for this, a short delay can be inserted after `datafiles` writes to the file system:

```python
import datafiles

datafiles.settings.WRITE_DELAY = 0.01  # seconds
```

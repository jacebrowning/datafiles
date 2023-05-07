# File Formats

The following formats are supported for serialization.

## YAML

By default, datafiles uses the [YAML language](https://yaml.org/) for serialization.
Any of the following file extensions will use this format:

- `.yml`
- `.yaml`
- (no extension)

Sample output:

```yaml
my_dict:
  value: 0
my_list:
  - value: 1
  - value: 2
my_bool: true
my_float: 1.23
my_int: 42
my_str: Hello, world!
```

Where possible, comments and whitespace are preserved in files as shown in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/main/notebooks/roundtrip_comments.ipynb).

## JSON

The [JSON language](https://www.json.org/) is also supported.
Any of the following file extensions will use this format:

- `.json`

Sample output:

```json
{
  "my_dict": {
    "value": 0
  },
  "my_list": [
    {
      "value": 1
    },
    {
      "value": 2
    }
  ],
  "my_bool": true,
  "my_float": 1.23,
  "my_int": 42,
  "my_str": "Hello, world!"
}
```

Additional examples can be found in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/main/notebooks/format_options.ipynb).

## TOML

The [TOML language](https://github.com/toml-lang/toml) is also supported.
Any of the following file extensions will use this format:

- `.toml`

Sample output:

```toml
my_bool = true
my_float = 1.23
my_int = 42
my_str = "Hello, world!"

[[my_list]]
value = 1

[[my_list]]
value = 2

[my_dict]
value = 0
```

Additional examples can be found in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/main/notebooks/format_options.ipynb).

## Custom Formats

Additional formats are supported through a registration system.

### Map Existing

To map one of the existing formatter classes to a new file extension:

```python hl_lines="4"
from datafile import datafile, formats


formats.register(".conf", formats.YAML)


@datafile("my-file-path.conf")
class MyConfig:
    ...
```
### New Format

To support new formats, extend the `datafiles.formats.Formatter` base class:

```python hl_lines="4"
from datafile import datafile, formats


class MyFormat(formats.Format):

    @classmethod
    def extensions(cls) -> list[str]:
        return [".my_ext"]

    @classmethod
    def deserialize(cls, file_object: IO) -> dict:
        # Read `file_object` and return a dictionary

    @classmethod
    def serialize(cls, data: dict) -> str:
        # Convert `data` to a string


formats.register(".my_ext", MyFormat)


@datafile("my-file-path.my_ext")
class MyConfig:
    ...
```

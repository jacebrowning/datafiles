The following formats are supported for serialization.

# YAML

By default, datafiles uses the [YAML language](https://yaml.org/) for serialization. Any of the following file extensions will use this format:

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

Where possible, comments and whitespace are preserved in files as shown in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/develop/notebooks/roundtrip_comments.ipynb).

# JSON

The [JSON language](https://www.json.org/) is also supported. Any of the following file extensions will use this format:

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

Additional examples can be found in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/develop/notebooks/format_options.ipynb).

# TOML

The [TOML language](https://github.com/toml-lang/toml) is also supported. Any of the following file extensions will use this format:

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

Additional examples can be found in this [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/develop/notebooks/format_options.ipynb).

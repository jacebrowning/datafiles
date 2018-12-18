# Requirements

* Make:
    * Windows: http://mingw.org/download/installer
    * Mac: http://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make
* Python 3.7+: `$ pyenv install`
* Poetry: https://poetry.eustace.io/docs/#installation
* Graphviz: http://www.graphviz.org/Download.php

To confirm these system dependencies are configured correctly:

```sh
$ bin/verchew
```

# Development

Manually run the tests and linters:

```sh
$ make test check
```
or keep them running on change:

```sh
$ make watch
```

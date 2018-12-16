# Datafiles: A File-based ORM for Dataclasses

Datafiles is bidirectional serialization library for Python [dataclasses](https://docs.python.org/3/library/dataclasses.html) that automatically synchronizes object instances to the filesystem.

[![Unix Build Status](https://img.shields.io/travis/jacebrowning/datafiles.svg?label=unix)](https://travis-ci.org/jacebrowning/datafiles)
[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/datafiles.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/datafiles)

## Installation

Because datafiles relies on dataclasses and type annotations, Python 3.7+ is required. Directly install it with `pip`:

```
$ pip install datafiles
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```
$ poetry add datafiles
```

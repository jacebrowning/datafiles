from dataclasses import dataclass
from typing import Dict, Optional

from .converters import Converter


@dataclass
class ModelMeta:
    datafile_attrs: Optional[Dict[str, Converter]] = None
    datafile_pattern: Optional[str] = None

    datafile_manual: bool = False
    datafile_defaults: bool = False
    datafile_auto_load: bool = True
    datafile_auto_save: bool = True
    datafile_auto_attr: bool = False

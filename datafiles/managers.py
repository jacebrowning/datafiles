import dataclasses
import json
from typing import Any, Dict, Optional

import log
from ruamel import yaml


class ModelManager:
    def __init__(self, cls):
        self.model = cls

    def all(self):
        raise NotImplementedError


class InstanceManager:
    def __init__(
        self, *, instance: Any, pattern: Optional[str], fields: Dict
    ) -> None:
        self._instance = instance
        self._pattern = pattern
        self.fields = fields

    @property
    def path(self) -> Optional[str]:
        if not self._pattern:
            log.debug(f'{self!r} has no path pattern')
            return None

        log.debug(f'Formatting {self._pattern!r} for {self._instance!r}')
        return self._pattern.format(self=self._instance)

    @property
    def data(self) -> Dict:
        data: Dict = dataclasses.asdict(self._instance)

        for key in list(data.keys()):
            if key not in self.fields:
                data.pop(key)

        return data

    @property
    def text(self) -> str:
        return self.get_text()

    def get_text(self, extension='yaml') -> str:
        if extension in {'yml', 'yaml'}:
            return yaml.round_trip_dump(self.data) if self.fields else ""
        if extension in {'json'}:
            return json.dumps(self.data)
        raise ValueError(f'Unsupported file extension: {extension!r}')

import dataclasses
from typing import Any, Dict, Optional

import log


class Manager:
    def __init__(
        self,
        synchronized_object: Any,
        path_pattern: Optional[str],
        mapped_fields: Dict,
    ):
        self._object = synchronized_object
        self._pattern = path_pattern
        self.fields = mapped_fields

    @property
    def path(self) -> Optional[str]:
        if not self._pattern:
            log.debug(f'{self!r} has no path pattern')
            return None

        log.debug(f'Formatting path {self._pattern!r} using {self._object!r}')
        return self._pattern.format(self=self._object)

    @property
    def data(self) -> Dict:
        data = dataclasses.asdict(self._object)

        for key in list(data.keys()):
            if key not in self.fields:
                data.pop(key)

        return data

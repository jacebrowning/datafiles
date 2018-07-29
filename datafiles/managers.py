import dataclasses
from typing import Any, Dict, Optional

import log


class Manager:
    def __init__(
        self, instance: Any, pattern: Optional[str], fields: Dict
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

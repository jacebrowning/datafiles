<h1>Logging</h1>

Logging is managed by [`minilog`](https://minilog.readthedocs.io), which configures logging automatically. Because the `@datafile()` decorator runs code at the module level, `datafiles` may prematurely configure logging for your application.

# Silence

To suppress this behavior, you should silence the `datafiles` logger before any models are defined:

```python hl_lines="4"
from datafiles import datafile
import log

log.silence('datafiles')

@datafile("inventory/items/{self.name}.yml")
class InventoryItem:

    name: str
    unit_price: float
    quantity_on_hand: int = 0

```

# Reset

If that's insufficient, you can reset logging back to its initial state after more models are defined:

```python hl_lines="6"
import log

from .models import InventoryItem

def main():
    log.reset()
    item = InventoryItem.objects.create("widget", 0.99)
```

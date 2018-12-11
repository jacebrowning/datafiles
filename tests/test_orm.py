from dataclasses import dataclass

from datafiles import sync


# This model is based on the example dataclass from:
# https://docs.python.org/3/library/dataclasses.html
@sync('../tmp/inventory/{self.pk}.yml')
@dataclass
class InventoryItem:
    pk: int
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand


def test_multiple_instances_are_distinct(expect, read, dedent):
    item_1 = InventoryItem(1, "Nuts", 0.23)
    item_2 = InventoryItem(2, "Bolts", 0.45, quantity_on_hand=100)

    expect(read('tmp/inventory/1.yml')) == dedent(
        """
        name: Nuts
        unit_price: 0.23
        """
    )
    expect(read('tmp/inventory/2.yml')) == dedent(
        """
        name: Bolts
        unit_price: 0.45
        quantity_on_hand: 100
        """
    )

    item_1.quantity_on_hand = 200
    item_2.unit_price = 0.34

    expect(read('tmp/inventory/1.yml')) == dedent(
        """
        name: Nuts
        unit_price: 0.23
        quantity_on_hand: 200
        """
    )
    expect(read('tmp/inventory/2.yml')) == dedent(
        """
        name: Bolts
        unit_price: 0.34
        quantity_on_hand: 100
        """
    )

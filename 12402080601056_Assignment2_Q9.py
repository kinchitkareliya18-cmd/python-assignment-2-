
class Inventory:
    def __init__(self, items=None):
        self.items = items if items is not None else {}

    def __add__(self, other):
        merged_items = self.items.copy()

        for item, quantity in other.items.items():
            merged_items[item] = merged_items.get(item, 0) + quantity

        return Inventory(merged_items)

    def __str__(self):
        if not self.items:
            return "Inventory is empty."

        result = "Inventory:\n"
        for item, quantity in sorted(self.items.items()):
            result += f"{item}: {quantity}\n"

        return result.rstrip()


def create_inventory(name):
    items = {}
    print(f"\nEnter items for {name} (type 'done' to finish).")

    while True:
        item = input("Item name: ").strip()

        if item.lower() == "done":
            break

        if not item:
            print("Item name cannot be empty.")
            continue

        try:
            quantity = int(input("Quantity: "))

            if quantity < 0:
                print("Quantity cannot be negative.")
                continue

            items[item] = items.get(item, 0) + quantity

        except ValueError:
            print("Please enter a valid whole number.")

    return Inventory(items)


inventory1 = create_inventory("Inventory 1")
inventory2 = create_inventory("Inventory 2")

merged_inventory = inventory1 + inventory2

print("\n--- Inventory 1 ---")
print(inventory1)

print("\n--- Inventory 2 ---")
print(inventory2)

print("\n--- Merged Inventory ---")
print(merged_inventory)

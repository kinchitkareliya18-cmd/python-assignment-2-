
import re
import os
import sys
from html.parser import HTMLParser
from decimal import Decimal, InvalidOperation


class ProductParser(HTMLParser):
    """Extract products from HTML using common product-related attributes."""

    def __init__(self):
        super().__init__()
        self.products = []
        self.current = {}
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # Product containers commonly use these classes or attributes.
        classes = attrs.get("class", "").lower().split()
        is_product = (
            tag in ("article", "li")
            and any("product" in c for c in classes)
        ) or "data-product" in attrs

        if is_product and not self.current:
            self.current = {"name": "", "price": "", "rating": ""}
            self.depth = 1
        elif self.current:
            self.depth += 1

        if self.current:
            itemprop = attrs.get("itemprop", "").lower()
            cls = attrs.get("class", "").lower()
            value = attrs.get("content") or attrs.get("data-price") or ""

            if itemprop == "name" or "product-name" in cls:
                self.current["name"] = value
            elif itemprop == "price" or "price" in cls:
                self.current["price"] = value
            elif itemprop == "ratingvalue" or "rating" in cls:
                self.current["rating"] = (
                    attrs.get("content")
                    or attrs.get("data-rating")
                    or value
                )

    def handle_data(self, data):
        if self.current:
            text = data.strip()
            if not text:
                return

            # Fill fields that were not provided as attributes.
            if not self.current["name"] and len(text) > 2:
                self.current["name"] = text
            elif not self.current["price"] and re.search(r"\d", text):
                self.current["price"] = text
            elif not self.current["rating"] and re.fullmatch(
                r"\s*[0-5](?:\.\d+)?\s*", text
            ):
                self.current["rating"] = text

    def handle_endtag(self, tag):
        if self.current:
            self.depth -= 1
            if self.depth <= 0:
                if all(self.current.values()):
                    self.products.append(self.current.copy())
                self.current = {}
                self.depth = 0


def normalize_price(value):
    """Convert a price such as '$1,299.00' to a Decimal."""
    cleaned = re.sub(r"[^0-9.]", "", value.replace(",", ""))
    try:
        price = Decimal(cleaned)
        return price if price >= 0 else None
    except InvalidOperation:
        return None


def parse_products(file_path):
    """Parse products from one local HTML file."""
    parser = ProductParser()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        parser.feed(file.read())

    results = []

    for product in parser.products:
        name = " ".join(product["name"].split())
        price = normalize_price(product["price"])

        try:
            rating = Decimal(product["rating"])
        except InvalidOperation:
            continue

        if (
            name
            and price is not None
            and Decimal("0") <= rating <= Decimal("5")
        ):
            results.append({
                "name": name,
                "price": price,
                "rating": rating
            })

    return results


def main():
    """Read HTML files, merge duplicates and rank products."""
    if len(sys.argv) > 1:
        print("Run this program without command-line arguments.")
        return

    try:
        k, n = map(
            int,
            input("Enter k (top products) and n (HTML files): ").split()
        )

        if not (1 <= k <= n <= 1000):
            print("Invalid input: require 1 <= k <= n <= 1000.")
            return

        products_by_name = {}

        for i in range(n):
            path = input(f"Enter path for HTML file {i + 1}: ").strip().strip('"')

            if not os.path.isfile(path):
                print(f"Error: File not found: {path}")
                return

            for product in parse_products(path):
                key = product["name"].casefold()

                # For duplicate names, keep the higher-rated listing;
                # break ties by keeping the lower price.
                existing = products_by_name.get(key)
                if (
                    existing is None
                    or product["rating"] > existing["rating"]
                    or (
                        product["rating"] == existing["rating"]
                        and product["price"] < existing["price"]
                    )
                ):
                    products_by_name[key] = product

        ranked = sorted(
            products_by_name.values(),
            key=lambda p: (-p["rating"], p["price"], p["name"].casefold())
        )

        print("\nTop Products")
        print("-" * 55)

        for product in ranked[:k]:
            print(
                f'{product["name"]} '
                f'{product["price"]:.2f} {product["rating"]}'
            )

        if not ranked:
            print("No valid products found.")

    except ValueError:
        print("Invalid input. Enter integers for k and n.")
    except OSError as error:
        print(f"File error: {error}")


if __name__ == "__main__":
    main()

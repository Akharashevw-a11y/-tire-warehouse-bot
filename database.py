import json

FILE = "stock.json"


def load_stock():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_stock(stock):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(stock, f, ensure_ascii=False, indent=4)


def add_tire(brand, size, season, quantity):
    stock = load_stock()

    stock.append({
        "brand": brand,
        "size": size,
        "season": season,
        "quantity": quantity
    })

    save_stock(stock)


def get_stock():
    return load_stock()


def remove_tire(brand, size, season, quantity):
    stock = load_stock()

    for tire in stock:
        if (
            tire["brand"] == brand
            and tire["size"] == size
            and tire["season"] == season
        ):
            tire["quantity"] -= quantity

            if tire["quantity"] <= 0:
                stock.remove(tire)

            save_stock(stock)
            return True

    return False

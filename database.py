import json

FILE = "stock.json"


def load_stock():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            stock = json.load(f)

            for tire in stock:
                if "photo" not in tire:
                    tire["photo"] = None

                if "price" not in tire:
                    tire["price"] = 0

                if "type" not in tire:
                    tire["type"] = ""

            return stock

    except:
        return []


def save_stock(stock):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(
            stock,
            f,
            ensure_ascii=False,
            indent=4
        )


def add_tire(
    brand,
    size,
    tire_type,
    quantity,
    price,
    photo=None
):

    stock = load_stock()

    stock.append({
        "brand": brand,
        "size": size,
        "type": tire_type,
        "quantity": quantity,
        "price": price,
        "photo": photo
    })

    save_stock(stock)


def get_stock():
    return load_stock()


def remove_tire(brand, size, tire_type, quantity):

    stock = load_stock()

    for tire in stock:

        if (
            tire["brand"].lower() == brand.lower()
            and tire["size"].lower() == size.lower()
            and tire["type"].lower() == tire_type.lower()
        ):

            tire["quantity"] -= quantity

            if tire["quantity"] <= 0:
                stock.remove(tire)

            save_stock(stock)
            return True

    return False


def find_tires(query):

    stock = load_stock()

    result = []

    words = query.lower().split()

    for tire in stock:

        text = (
            f"{tire['brand']} "
            f"{tire['size']} "
            f"{tire['type']}"
        ).lower()

        if all(word in text for word in words):
            result.append(tire)

    return result


import json
import os
import tempfile

FILE = "stock.json"


def load_stock():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            stock = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise RuntimeError(
            f"Не удалось прочитать {FILE}. "
            "Файл не изменён, чтобы защитить данные."
        ) from e

    if not isinstance(stock, list):
        raise RuntimeError(
            f"Файл {FILE} содержит неверный формат. "
            "Файл не изменён."
        )

    for tire in stock:
        if not isinstance(tire, dict):
            raise RuntimeError("В stock.json обнаружена неверная запись.")

        tire.setdefault("photo", None)
        tire.setdefault("price", 0)
        tire.setdefault("type", "")
        tire.setdefault("quantity", 0)

    return stock


def save_stock(stock):
    directory = os.path.dirname(os.path.abspath(FILE))
    fd, temp_file = tempfile.mkstemp(
        prefix="stock_",
        suffix=".tmp",
        dir=directory
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(
                stock,
                f,
                ensure_ascii=False,
                indent=4
            )
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_file, FILE)

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


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
            tire.get("brand", "").casefold() == brand.casefold()
            and tire.get("size", "").replace(" ", "").casefold()
            == size.replace(" ", "").casefold()
            and tire.get("type", "").casefold()
            == tire_type.casefold()
        ):
            if quantity <= 0 or quantity > tire.get("quantity", 0):
                return False

            tire["quantity"] -= quantity

            if tire["quantity"] == 0:
                stock.remove(tire)

            save_stock(stock)
            return True

    return False


def find_tires(query):
    stock = load_stock()
    words = query.casefold().split()

    result = []

    for tire in stock:
        text = (
            f"{tire.get('brand', '')} "
            f"{tire.get('size', '')} "
            f"{tire.get('type', '')}"
        ).casefold()

        text = text.replace(" ", "")

        if all(word.replace(" ", "") in text for word in words):
            result.append(tire)

    return result

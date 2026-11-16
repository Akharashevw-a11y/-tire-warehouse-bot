
import os
from supabase import create_client

_client = None


def get_client():
    global _client

    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError(
                "Не найдены SUPABASE_URL или SUPABASE_KEY в GitHub Secrets"
            )

        _client = create_client(url, key)

    return _client


def load_stock():
    response = (
        get_client()
        .table("TRS")
        .select("*")
        .order("id")
        .execute()
    )

    return [
        {
            "id": tire["id"],
            "brand": tire.get("brand", ""),
            "size": tire.get("size", ""),
            "type": tire.get("type", ""),
            "quantity": tire.get("quantity", 0),
            "price": tire.get("price", 0),
            "photo": tire.get("photo"),
        }
        for tire in response.data
    ]


def save_stock(stock):
    client = get_client()

    for tire in stock:
        data = {
            "brand": tire.get("brand", ""),
            "size": tire.get("size", ""),
            "type": tire.get("type", ""),
            "quantity": tire.get("quantity", 0),
            "price": tire.get("price", 0),
            "photo": tire.get("photo"),
        }

        if tire.get("id") is not None:
            client.table("TRS").update(data).eq(
                "id", tire["id"]
            ).execute()
        else:
            client.table("TRS").insert(data).execute()


def add_tire(
    brand,
    size,
    tire_type,
    quantity,
    price,
    photo=None
):
    get_client().table("TRS").insert({
        "brand": brand,
        "size": size,
        "type": tire_type,
        "quantity": quantity,
        "price": price,
        "photo": photo,
    }).execute()


def get_stock():
    return load_stock()


def remove_tire(brand, size, tire_type, quantity):
    stock = load_stock()

    for tire in stock:
        if (
            tire["brand"].casefold() == brand.casefold()
            and tire["size"].replace(" ", "").casefold()
            == size.replace(" ", "").casefold()
            and tire["type"].casefold() == tire_type.casefold()
        ):
            if quantity <= 0 or quantity > tire["quantity"]:
                return False

            new_quantity = tire["quantity"] - quantity

            if new_quantity == 0:
                get_client().table("TRS").delete().eq(
                    "id", tire["id"]
                ).execute()
            else:
                get_client().table("TRS").update({
                    "quantity": new_quantity
                }).eq("id", tire["id"]).execute()

            return True

    return False


def find_tires(query):
    stock = load_stock()
    words = query.casefold().split()
    result = []

    for tire in stock:
        text = (
            f"{tire['brand']} "
            f"{tire['size']} "
            f"{tire['type']}"
        ).casefold().replace(" ", "")

        if all(word.replace(" ", "") in text for word in words):
            result.append(tire)

    return result

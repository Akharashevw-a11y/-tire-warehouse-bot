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

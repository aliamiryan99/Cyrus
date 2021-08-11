

def get_fib_levels(start_price, end_price):
    fib_levels = [-0.618, -0.272, 0, 0.382, 0.5, 0.618, 0.786, 1, 1.618]
    price_fib_levels = {}
    for fib_level in fib_levels:
        price_fib_levels[fib_level] = end_price - fib_level * (end_price - start_price)
    return price_fib_levels



def get_strong_number(price, base, pip):
    return price - (((price * 10 ** pip) % base) / 10 ** pip)


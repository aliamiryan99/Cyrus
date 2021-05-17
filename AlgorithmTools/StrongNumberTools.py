

def get_strong_number(point_price):
    strong_numbers = [200, 500, 800]
    trim_price = point_price % 1000
    strong = 0
    for i in range(len(strong_numbers)):
        if trim_price - strong_numbers[i] > 0:
            strong = strong_numbers[max(0, i - 1)]
            break
    return point_price - (point_price % strong)


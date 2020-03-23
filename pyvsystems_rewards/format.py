
def format_as_vsys(amount):
    abs_amount = abs(amount)
    whole = int(abs_amount / 100000000)
    fraction = abs_amount % 100000000

    if amount < 0:
        whole *= -1

    return f'{whole}.{str(fraction).rjust(8, "0")}'

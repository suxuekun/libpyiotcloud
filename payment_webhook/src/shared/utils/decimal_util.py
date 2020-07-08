from decimal import Decimal

TWOPLACES = Decimal('0.01')

def two_decimal_str(num):
    return str(Decimal(num).quantize(TWOPLACES))
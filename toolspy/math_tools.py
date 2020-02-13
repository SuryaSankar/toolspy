from __future__ import absolute_import
import math
from decimal import Decimal


def hypotenuse(x, y):
    return math.sqrt(x**2 + y**2)


def round_float(value, precision=2):
    if value is None:
        return None
    return math.ceil(value*(10**precision))/(10**precision)


def percentage(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return None
    value = float(numerator)*100/float(denominator)
    return math.ceil(value*100)/100


def percentage_markup(original, percent):
    return monetize(original + (Decimal(percent) / 100) * original)


def percentage_markdown(original, percent):
    if original is None:
        return None
    return original / (1 + Decimal(percent) / 100)


def null_safe_sum(*values):
    result = 0
    for val in values:
        if val is not None:
            result += val
    return result


def discount_percent(original_price, new_price):
    return percentage(original_price-new_price, original_price)


def quantize(number, decimal_places=2):
    if number is None:
        return None
    return Decimal(number).quantize(
        Decimal(1) / 10**decimal_places
    )

def monetize(number):
    return quantize(number, 2)


def financial_year(dt):
    def fy_format(y1, y2):
        return "{0}-{1}".format(y1, y2)

    if dt.month <= 3:
        return fy_format(dt.year - 1, dt.year)
    return fy_format(dt.year, dt.year + 1)


def is_number(s):
    if isinstance(s, int) or isinstance(s, float) or isinstance(s, Decimal):
        return True
    else:
        try:
            int(s)
            return True
        except:
            try:
                float(s)
                return True
            except:
                return False


def is_int(s):
    if isinstance(s, int):
        return True
    else:
        try:
            int(s)
            return True
        except:
            return False

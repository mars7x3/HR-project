from tariffs.models import Tariff


def check_amount(tariffs):
    amount = int()
    for t in tariffs:
        day_price = t.get('day_and_price')
        tariff = Tariff.objects.get(id=t.get('tariff'))
        day_and_prices = tariff.day_and_price.get(id=day_price)
        pbp_price = day_and_prices.pbp_price
        price = day_and_prices.price

        if pbp_price:
            amount += int(t.get('count')) * pbp_price
        elif price:
            amount += price

    return amount

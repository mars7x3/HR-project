from django.contrib import admin

from .models import *


admin.site.register(PriceList)
admin.site.register(UserTariffFunction)
admin.site.register(AccessToResume)
admin.site.register(MyTariff)


class DayAndPriceInline(admin.TabularInline):
    model = DayAndPrice
    max_num = 10
    extra = 1


@admin.register(Tariff)
class AboutAdmin(admin.ModelAdmin):
    inlines = [DayAndPriceInline]



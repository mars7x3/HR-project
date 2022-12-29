from django.contrib import admin

from .models import Wallet, WalletHistory

admin.site.register(Wallet)
admin.site.register(WalletHistory)



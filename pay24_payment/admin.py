from django.contrib import admin
from .models import *


@admin.register(Pay24TransactionReceipt)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'txn_id', 'wallet', 'amount', 'result', 'created_at')
    list_display_links = ('id', 'txn_id', 'wallet', 'amount', 'result', 'created_at')
    search_fields = ('wallet', 'txn_id', 'amount', 'result', 'created_at')


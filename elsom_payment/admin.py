from django.contrib import admin
from .models import *


@admin.register(TransactionReceipt)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'wallet', 'amount', 'created_at')
    list_display_links = ('id', 'status', 'wallet', 'amount', 'created_at')
    search_fields = ('id', 'wallet', 'status', 'created_at', 'amount')




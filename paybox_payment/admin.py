from django.contrib import admin

from paybox_payment.models import PayBoxTransactionReceipt


@admin.register(PayBoxTransactionReceipt)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'pg_amount', 'created_at')
    list_display_links = ('id', 'wallet', 'pg_amount', 'created_at')
    search_fields = ('wallet', 'created_at', 'pg_amount')



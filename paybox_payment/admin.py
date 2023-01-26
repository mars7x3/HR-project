from django.contrib import admin

from paybox_payment.models import PayBoxTransactionReceipt


@admin.register(PayBoxTransactionReceipt)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'pg_result', 'wallet', 'pg_amount', 'created_at')
    list_display_links = ('id', 'pg_result', 'wallet', 'pg_amount', 'created_at')
    search_fields = ('id', 'wallet', 'pg_result', 'created_at', 'pg_amount')



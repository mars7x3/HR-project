from django.db import models


class PayBoxTransactionReceipt(models.Model):
    wallet = models.CharField(max_length=100, blank=True, null=True)
    pg_order_id = models.CharField(max_length=100, blank=True, null=True)
    pg_payment_id = models.CharField(max_length=100, blank=True, null=True)
    pg_amount = models.CharField(max_length=100, blank=True, null=True)
    pg_currency = models.CharField(max_length=10, blank=True, null=True)
    pg_net_amount = models.CharField(max_length=100, blank=True, null=True)
    pg_ps_amount = models.CharField(max_length=100, blank=True, null=True)
    pg_ps_full_amount = models.CharField(max_length=100, blank=True, null=True)
    pg_ps_currency = models.CharField(max_length=10, blank=True, null=True)
    pg_description = models.CharField(max_length=200, blank=True, null=True)
    pg_result = models.CharField(max_length=2, blank=True, null=True)
    pg_payment_date = models.CharField(max_length=100, blank=True, null=True)
    pg_can_reject = models.CharField(max_length=2, blank=True, null=True)
    pg_user_phone = models.CharField(max_length=50, blank=True, null=True)
    pg_user_contact_email = models.CharField(max_length=150, blank=True, null=True)
    pg_need_email_notification = models.CharField(max_length=150, blank=True, null=True)
    pg_testing_mode = models.CharField(max_length=2, blank=True, null=True)
    pg_captured = models.CharField(max_length=2, blank=True, null=True)
    pg_card_pan = models.CharField(max_length=50, blank=True, null=True)
    pg_card_exp = models.CharField(max_length=10, blank=True, null=True)
    pg_card_owner = models.CharField(max_length=50, blank=True, null=True)
    pg_card_brand = models.CharField(max_length=10, blank=True, null=True)
    pg_salt = models.CharField(max_length=150, blank=True, null=True)
    pg_sig = models.CharField(max_length=150, blank=True, null=True)
    pg_payment_method = models.CharField(max_length=50, blank=True, null=True)
    pg_need_phone_notification = models.CharField(max_length=2, blank=True, null=True)
    pg_failure_code = models.CharField(max_length=50, blank=True, null=True)
    pg_failure_description = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wallet

    class Meta:
        ordering = ['-id']




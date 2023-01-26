from django.db import models


class TransactionReceipt(models.Model):
    wallet = models.CharField(max_length=50)
    user_phone = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=2, default='1')
    message = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']





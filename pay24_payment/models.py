from django.db import models


class Pay24TransactionReceipt(models.Model):
    wallet = models.CharField(max_length=50)
    comment = models.CharField(max_length=100, blank=True, null=True)
    txn_id = models.CharField(max_length=20, blank=True, null=True)
    result = models.CharField(max_length=3, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    txn_date = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']






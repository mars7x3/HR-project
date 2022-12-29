from django.db import models


class TransactionReceipt(models.Model):
    wallet = models.CharField(max_length=100)
    user_phone = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=100, blank=True, null=True)
    cashier_no = models.CharField(max_length=100, default='elsom_v1.0')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']


class TransactionID(models.Model):
    transaction_receipt = models.ForeignKey(TransactionReceipt, on_delete=models.CASCADE,
                                            related_name='transaction_ids')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']


class CheckTransaction(models.Model):
    transaction_receipt = models.ForeignKey(TransactionReceipt, on_delete=models.CASCADE,
                                            related_name='transaction_check')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']



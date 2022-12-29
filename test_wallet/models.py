from django.db import models

from accounts.models import MyUser


class Wallet(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='wallet')
    amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)

    def __str__(self):
        return self.user.username


class WalletHistory(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='histories')
    client = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=50)
    amount = models.CharField(max_length=100)
    manager = models.CharField(max_length=100, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    is_dumps = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.wallet} | {self.status}{self.amount} | {self.manager if self.manager else ""} | ' \
               f'{self.created_at}'





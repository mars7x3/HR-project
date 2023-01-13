from django.db import models
from accounts.models import MyUser, Manager
from test_wallet.models import Wallet
from ckeditor.fields import RichTextField


class Plan(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='manager_plan')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Сумма')
    done = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Выполнено')

    def __str__(self):
        return f'{self.id} - {self.manager}'

    class Meta:
        ordering = ['-id']


class PayHistory(models.Model):
    wallet = models.CharField(max_length=100)
    company = models.CharField(max_length=200, blank=True, null=True)
    payment = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.wallet} | {self.payment} | {self.amount}'

    class Meta:
        ordering = ['-id']


class TermsHistory(models.Model):
    company = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True)
    tariff = models.CharField(max_length=300)
    tariff_price = models.DecimalField(max_digits=15, decimal_places=2)
    tariff_dead_time = models.DateTimeField()
    status = models.CharField(max_length=100, default='None')
    comment = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.company}'

    class Meta:
        ordering = ['-id']


class LimitsHistory(models.Model):
    company = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True)
    tariff = models.CharField(max_length=2000)
    tariff_price = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=100, default='None')
    comment = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.company}'

    class Meta:
        ordering = ['-id']


class DumpsHistory(models.Model):
    company = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True)
    last_transaction = models.DateTimeField(auto_now=True)
    last_transaction_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=100, default='None')
    comment = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.company}'

    class Meta:
        ordering = ['-id']


class Debtors(models.Model):
    company = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='debtors')
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True)
    transaction_amount = models.IntegerField()
    status = models.CharField(max_length=100, default='None')
    comment = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.company}'

    class Meta:
        ordering = ['-id']


class EntityAllHistory(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='all_history')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    comment = models.TextField()
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']


class CallRequest(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True)
    company = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.company.username} - {self.status} - {self.created_at}'

    class Meta:
        ordering = ['-id']


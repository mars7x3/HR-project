# Generated by Django 4.1 on 2023-01-12 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paybox_payment', '0006_payboxtransactionreceipt_pg_failure_code_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payboxtransactionreceipt',
            name='amount',
        ),
    ]

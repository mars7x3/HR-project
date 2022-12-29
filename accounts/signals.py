from django.db.models.signals import post_save
from django.dispatch import receiver

from tariffs.models import UserTariffFunction
from test_wallet.models import Wallet
from .utils import generate_username, send_pwd_and_username
from accounts.models import MyUser, EntityProfile, Manager, PasswordTest


@receiver(post_save, sender=MyUser)
def generate_username_pwd(sender, instance, created, **kwargs):
    if created:
        instance.username = generate_username(instance.id)
        # password = generate_pwd()
        PasswordTest.objects.create(username=instance.username, password=instance.password, email=instance.email)
        send_pwd_and_username(instance.username, instance.password, instance.email)
        instance.set_password(instance.password)
        user_statuses = ['applicant', 'main', 'manager', 'moderator']
        personals = ['main', 'manager', 'moderator']

        if not instance.user_status:
            instance.user_status = 'applicant'
        if instance.user_status not in user_statuses and not instance.is_superuser:
            EntityProfile.objects.create(user=instance, company=instance.username)
        if instance.user_status not in personals and not instance.is_superuser:
            Wallet.objects.create(user=instance)
            UserTariffFunction.objects.create(user=instance)
        if instance.user_status == 'manager' or instance.user_status == 'main':
            Manager.objects.create(manager=instance, telegram='@telegram', whatsapp='+996', email=instance.email,
                                   manager_name=instance.username)

        instance.save()

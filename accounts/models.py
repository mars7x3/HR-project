from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.conf import settings

from accounts.utils import generate_activation_code, send_activation_code


# from accounts.utils import generate_activation_code, send_activation_code


class EmailAndCode(models.Model):
    email = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    @property
    def dead_time(self) -> timedelta:
        return self.created_at + timedelta(hours=settings.CODE_DEAD_HOURS)

    def check_time(self) -> bool:
        if now() >= self.dead_time:
            return False
        return True

    @classmethod
    def send_confirm_code(cls, email: str):
        activation_code = generate_activation_code()
        email_code = EmailAndCode.objects.filter(email=email)
        if email_code.exists():
            send_activation_code(email, activation_code)
            email_code.update(email=email, code=activation_code)
        else:
            send_activation_code(email, activation_code)
            email_code.create(email=email, code=activation_code)


class MyUser(AbstractUser):
    STATUS = (
        ('applicant', 'Ищу работу'),
        ('entity', 'Ищу сотрудника'),
        ('main', 'Полный'),
        ('manager', 'Менеджер'),
        ('moderator', 'Модератор'),

    )
    email = models.EmailField(_("email address"), unique=True)
    user_status = models.CharField(choices=STATUS, max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='user_avatar', blank=True, null=True)

    def __str__(self):
        return f'{self.email or self.username} - {self.id}'


class EntityProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='entity_profile')
    image = models.FileField(upload_to='profile-images', blank=True)
    full_name = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    company = models.CharField(max_length=300, blank=True, null=True)
    inn = models.CharField(max_length=20, blank=True, null=True)
    activity = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    site = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    company_type = models.BooleanField(default=True)
    social_media_type = models.CharField(max_length=20, blank=True, null=True)
    social_media = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=200, blank=True, null=True)
    facebook = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    moderation_comment = models.TextField(blank=True, null=True)
    is_moderation = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id} - {self.company}'

    class Meta:
        ordering = ('-id',)


class EntityProfilePhone(models.Model):
    profile = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name='entity_phones')
    phone = models.CharField(max_length=20)


class EntityPersonal(models.Model):
    profile = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name='entity_personals')
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name


class EntityRequisite(models.Model):
    profile = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name='entity_requisites')
    entity_name = models.CharField(max_length=200, verbose_name='Название юр лица')
    inn = models.CharField(max_length=50, verbose_name='ИНН')
    okpo = models.CharField(max_length=100, verbose_name='ОКПО')
    mailing_address = models.CharField(max_length=100, verbose_name='Почтовый адрес')
    entity_address = models.CharField(max_length=100, verbose_name='Юридический адрес')
    bik = models.CharField(max_length=20, verbose_name='БИК')
    bank_name = models.CharField(max_length=100, verbose_name='Название банка')
    checking_account = models.CharField(max_length=100, verbose_name='Расчетный счет')
    gni = models.CharField(max_length=100, verbose_name='ГНИ')
    contact = models.CharField(max_length=100, verbose_name='Контактное лицо')
    email = models.CharField(max_length=100, verbose_name='E-mail для отправки счетов')
    info = models.TextField(verbose_name='Дополнительная информация')


class Document(models.Model):
    profile = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name='entity_documents')
    created_add = models.DateTimeField(auto_now=True)
    document = models.FileField(upload_to='entity-documents', verbose_name='Документ')


class Manager(models.Model):
    profiles = models.ManyToManyField(EntityProfile, blank=True, related_name='manager')
    manager = models.OneToOneField(MyUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='manager')
    manager_name = models.CharField(max_length=100)
    telegram = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.id} - {self.manager}'


class ProfileComment(models.Model):
    profile = models.ForeignKey(EntityProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='comments')
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True, related_name='profile_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PasswordTest(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.id} - {self.username} - {self.email}'

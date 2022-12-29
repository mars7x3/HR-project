from django.db import models

from accounts.models import MyUser
from resume.models import Specialization, Resume


class UserTariffFunction(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='user_tariff_function')
    contact_amount = models.IntegerField(default=0, verbose_name='Доступ к резюме поштучно')
    contact_amount_dead_time = models.DateTimeField(verbose_name='Время доступ к резюме поштучно', blank=True, null=True)
    contact_rubric = models.BooleanField(default=False, verbose_name='Доступ к резюме в рубрике')
    contact_rubric_list = models.ManyToManyField(Specialization, related_name='user_tariff_functions', blank=True,
                                                 verbose_name='Рубрика для резюме')
    contact_rubric_dead_time = models.DateTimeField(verbose_name='Время доступ к резюме в рубрике', blank=True, null=True)
    banner = models.BooleanField(blank=True, null=True, verbose_name='Банер')
    banner_is_active = models.BooleanField(default=False)
    banner_moderation = models.BooleanField(default=False, verbose_name='Модерация банера')
    banner_tariff_title = models.CharField(max_length=300, blank=True, null=True)
    banner_link = models.CharField(max_length=300, blank=True, null=True, verbose_name='URL банера')
    banner_image = models.FileField(upload_to='banner', blank=True, null=True, verbose_name='Фото Банера')
    banner_dead_time = models.DateTimeField(verbose_name='Время Банера', blank=True, null=True)
    banner_rubric_list = models.ManyToManyField(Specialization, related_name='user_tariff_functions_banner', blank=True,
                                                verbose_name='Рубрика для банера')
    employer = models.BooleanField(default=False, verbose_name='Ведущие компании')
    employer_is_active = models.BooleanField(default=False)
    employer_moderation = models.BooleanField(default=False, verbose_name=' Модерация ведущие компании')
    employer_tariff_title = models.CharField(max_length=300, blank=True, null=True)
    employer_title = models.CharField(max_length=200, blank=True, null=True, verbose_name='Название Ведущие компании')
    employer_link = models.CharField(max_length=200, verbose_name='Ссылка Ведущие компании', blank=True, null=True)
    employer_image = models.ImageField(upload_to='banner', blank=True, null=True, verbose_name='Лого Ведущие компании')
    employer_dead_time = models.DateTimeField(verbose_name='Время Ведущие компании', blank=True, null=True)
    vip_vacancy_count_rubrics = models.IntegerField(default=0)
    vip_vacancy_count_all_rubrics = models.IntegerField(default=0)
    vip_vacancy_deed_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.id}. {self.user.username}'

    class Meta:
        verbose_name_plural = 'Подключенные тарифы'
        verbose_name = 'Подключенные тарифы'


class AccessToResume(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='access_to_resumes')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='access_to_resumes')

    def __str__(self):
        return f'{self.user.username} - {self.resume}'


class PriceList(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название тарифа')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Прайс лист'
        verbose_name = 'Прайс лист'


class Tariff(models.Model):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name='tariffs')
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return f'{self.id} - {self.title}'


class DayAndPrice(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, related_name='day_and_price')
    day = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(blank=True, null=True, max_digits=15, decimal_places=2)
    pbp_price = models.DecimalField(blank=True, null=True, max_digits=15, decimal_places=2)


class MyTariff(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='my_tariffs')
    tariff = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    dead_time = models.DateTimeField(blank=True, null=True)
    is_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} | {self.tariff} | {self.price}KGS | {self.dead_time}'

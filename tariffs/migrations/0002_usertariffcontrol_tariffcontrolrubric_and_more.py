# Generated by Django 4.1 on 2023-01-25 08:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resume', '0006_alter_workexperience_options'),
        ('tariffs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTariffControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_amount', models.IntegerField(default=0, verbose_name='Доступ к резюме поштучно')),
                ('contact_amount_dead_time', models.DateTimeField(auto_now_add=True, verbose_name='Время доступ к резюме поштучно')),
                ('vip_vacancy_count_rubrics', models.IntegerField(default=0)),
                ('vip_vacancy_count_all_rubrics', models.IntegerField(default=0)),
                ('vip_vacancy_deed_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tariff_control', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Подключенные тарифы Контроль',
                'verbose_name_plural': 'Подключенные тарифы Контроль',
            },
        ),
        migrations.CreateModel(
            name='TariffControlRubric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dead_time', models.DateTimeField(auto_now_add=True)),
                ('rubric', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tс_contacts', to='resume.specialization')),
                ('tariff_control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tс_contact_rubrics', to='tariffs.usertariffcontrol')),
            ],
        ),
        migrations.CreateModel(
            name='TariffControlEmployer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('is_moderation', models.BooleanField(default=False, verbose_name=' Модерация ведущие компании')),
                ('title', models.CharField(max_length=200, verbose_name='Название Ведущие компании')),
                ('link', models.CharField(blank=True, max_length=200, null=True, verbose_name='Ссылка Ведущие компании')),
                ('image', models.ImageField(blank=True, null=True, upload_to='banner', verbose_name='Лого Ведущие компании')),
                ('dead_time', models.DateTimeField(auto_now_add=True, verbose_name='Время Ведущие компании')),
                ('tariff_control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tс_employer', to='tariffs.usertariffcontrol')),
            ],
        ),
        migrations.CreateModel(
            name='TariffControlBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('is_moderation', models.BooleanField(default=False, verbose_name='Модерация банера')),
                ('tariff_title', models.CharField(blank=True, max_length=300, null=True)),
                ('link', models.CharField(blank=True, max_length=300, null=True, verbose_name='URL банера')),
                ('image', models.FileField(blank=True, null=True, upload_to='banner', verbose_name='Фото Банера')),
                ('dead_time', models.DateTimeField(auto_now_add=True)),
                ('rubric', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tс_banners', to='resume.specialization')),
                ('tariff_control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tс_banner', to='tariffs.usertariffcontrol')),
            ],
        ),
    ]

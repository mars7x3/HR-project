
from django.utils import timezone
from vacancy.models import Vacancy
from main.celery import app


@app.task()
def vip_vacancies_update():
    vip_vacancies = Vacancy.objects.filter(vip_status=False, is_active=True, archive=False)
    if vip_vacancies.exists():
        vip_vacancy = vip_vacancies.last()
        vip_vacancy.up_time = timezone.now()
        vip_vacancy.save()




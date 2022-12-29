from django.utils import timezone

from tariffs.models import UserTariffFunction, AccessToResume


def check_dead_time_tariff(user):
    user_tariff = user.user_tariff_function
    if user_tariff.contact_amount_dead_time < timezone.now():
        user_tariff.contact_amount = 0
        user_tariff.save()
        AccessToResume.objects.filter(user=user_tariff.user).delete()







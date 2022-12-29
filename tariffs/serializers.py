from rest_framework import serializers

from accounts.models import EntityProfile, MyUser
from vacancy.models import Vacancy
from vacancy.serializers import ProfileSerializer
from .models import UserTariffFunction, MyTariff, PriceList, Tariff, DayAndPrice


class EmployerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTariffFunction
        fields = ('employer_title', 'employer_link', 'employer_image', 'employer_is_active',
                  'employer_tariff_title')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if EntityProfile.objects.get(user=instance.user):
            representation['vacancies_count'] = MyUser.objects.get(id=instance.user.id).vacancies.all().count()

        return representation


class BannerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTariffFunction
        fields = ('banner_link', 'banner_image', 'banner_rubric_list', 'banner_is_active', 'banner_tariff_title')


class MyTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyTariff
        fields = "__all__"


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tariffs'] = TariffSerializer(instance.tariffs, context=self.context, many=True).data

        return representation


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['day_and_price'] = DayAndPriceSerializer(instance.day_and_price, context=self.context, many=True).data

        return representation

class DayAndPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayAndPrice
        fields = "__all__"
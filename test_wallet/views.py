import datetime

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAuthorPermission
from myadmin.models import EntityAllHistory, LimitsHistory
from myadmin.utils import plan_done, pay_history, delete_debtor
from tariffs.models import MyTariff, Tariff
from vacancy.models import Vacancy

from .serializers import *
from .models import Wallet, WalletHistory
from .utils import check_amount


class WalletListView(generics.ListAPIView):
    queryset = Wallet.objects.filter()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated, IsAuthorPermission]


# class PurchaseTransaction(APIView):
#     permission_classes = [IsAuthenticated, IsAuthorPermission]
#
#     def post(self, request):
#         tariffs = request.data.get("tariffs")
#         wallet = request.user.wallet
#         user = request.user
#         amount = int()
#         for t in tariffs:
#             if t.get('title') == 'Резюме поштучно (1 резюме)':
#                 amount += Tariff.objects.get(title=t.get('title')).day_and_price.all()[0].pbp_price *\
#                           t.get('count')
#                 # resume_count = int(t.get('count'))
#                 # user_tariff_func = user.user_tariff_function
#                 # user_tariff_func.contact_amount += resume_count
#                 # date = datetime.datetime(2100, 1, 1, 12, 00, 00)
#                 # user_tariff_func.contact_amount_dead_time = date
#                 # user_tariff_func.save()
#
#             if t.get('title') == 'Доступ к рубрике резюме':
#                 amount += Tariff.objects.get(title=t.get('title')).day_and_price.get(day=t.get('day')).pbp_price
#                 # resume_rubrics = t.get('rubrics')
#                 # days = int(t.get('days'))
#                 # user_tariff_func = user.user_tariff_function
#                 # user_tariff_func.contact_rubric = True
#                 # date = timezone.now() + datetime.timedelta(days=days)
#                 # user_tariff_func.contact_rubric_dead_time = date
#                 # user_tariff_func.save()
#                 # for r in resume_rubrics:
#                 #     user_tariff_func.contact_rubric_list.add(r)
#                 #     user_tariff_func.save()
#
#         if amount and wallet:
#             result = wallet.amount - int(amount)
#
#             if result < 0:
#                 return Response({"error": "Insufficient funds!"}, status=status.HTTP_400_BAD_REQUEST)
#
#
#
#             wallet.amount = result
#             WalletHistory.objects.create(wallet=wallet, status='-', amount=amount, client=request.user.username)
#             MyTariff.objects.bulk_create([MyTariff(user=user, tariff=tar.get('title'),
#                                                    price=tar.get('price')) for tar in tariffs])
#             wallet.save()
#             return Response({"detail": "Success!"}, status=status.HTTP_200_OK)
#
#         return Response({"error": "Amount or wallet required!"}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseTransaction(APIView):
    permission_classes = [IsAuthenticated, IsAuthorPermission]

    def post(self, request):
        try:
            tariffs = request.data.get("tariffs")
            wallet = request.user.wallet
            user = request.user
            amount = check_amount(tariffs)

            result = wallet.amount - amount
            if result < 0:
                tariffs_title = []
                for d in tariffs:
                    tariff = Tariff.objects.get(id=d.get('tariff'))
                    tariffs_title.append(tariff.title)
                tariffs_title = ', '.join(tariffs_title)

                LimitsHistory.objects.create(company=user, manager=user.entity_profile.manager.all()[0],
                                             tariff=tariffs_title, tariff_price=amount)
                return Response({"error": "У вас недостаточно средств на балансе!"}, status=status.HTTP_400_BAD_REQUEST)

            for t in tariffs:
                day_price = t.get('day_and_price')
                tariff = Tariff.objects.get(id=t.get('tariff'))
                day_and_prices = tariff.day_and_price.get(id=day_price)
                pbp_price = day_and_prices.pbp_price
                price = day_and_prices.price
                user_tariff_func = user.user_tariff_function

                if tariff.id == 1:
                    resume_count = int(t.get('count'))
                    total_price = resume_count * pbp_price
                    date = timezone.now() + datetime.timedelta(days=30)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=total_price, dead_time=date)
                    user_tariff_func.contact_amount += resume_count
                    user_tariff_func.contact_amount_dead_time = date
                    user_tariff_func.save()

                elif tariff.id == 2 or tariff.id == 3:
                    date = timezone.now() + datetime.timedelta(days=day_and_prices.day)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=price, dead_time=date)
                    resume_rubrics = t.get('rubrics')
                    user_tariff_func.contact_rubric = True
                    user_tariff_func.contact_rubric_dead_time = date
                    user_tariff_func.save()
                    for r in resume_rubrics:
                        user_tariff_func.contact_rubric_list.add(r)
                        user_tariff_func.save()

                elif tariff.id == 4 or tariff.id == 6:
                    date = timezone.now() + datetime.timedelta(days=day_and_prices.day)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=price, dead_time=date)
                    user_tariff_func.banner_dead_time = date
                    user_tariff_func.banner = True
                    user_tariff_func.banner_is_active = False
                    user_tariff_func.banner_tariff_title = tariff.title
                    user_tariff_func.save()
                    rubrics = t.get('banner_rubric_list')
                    if len(rubrics) > 1:
                        user_tariff_func.banner_rubric_list.clear()
                        for r in rubrics:
                            user_tariff_func.banner_rubric_list.add(r)
                            user_tariff_func.save()
                    else:
                        for r in rubrics:
                            user_tariff_func.banner_rubric_list.clear()
                            user_tariff_func.banner_rubric_list.add(r)
                            user_tariff_func.save()

                elif tariff.id == 5:
                    date = timezone.now() + datetime.timedelta(days=day_and_prices.day)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=price, dead_time=date)
                    user_tariff_func.employer_dead_time = date
                    user_tariff_func.employer = True
                    user_tariff_func.employer_is_active = False
                    user_tariff_func.employer_tariff_title = tariff.title
                    user_tariff_func.save()

                elif tariff.id == 7:
                    vacancy_id = t.get('vacancy')
                    date = timezone.now() + datetime.timedelta(days=day_and_prices.day)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=price, dead_time=date)
                    vacancy = Vacancy.objects.get(id=vacancy_id)
                    vacancy.vip_status = True
                    vacancy.up_status_10 = True
                    vacancy.vip_dead_time = date
                    vacancy.save()

                elif tariff.id == 8 or tariff.id == 9:
                    vacancy_id = t.get('vacancy')
                    date = timezone.now() + datetime.timedelta(days=day_and_prices.day)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=price, dead_time=date)
                    vacancy = Vacancy.objects.get(id=vacancy_id)
                    vacancy.vip_status = True
                    vacancy.up_status_10 = True
                    vacancy.vip_dead_time = date
                    vacancy.save()
                    for r in t.get('rubrics'):
                        vacancy.vip_rubrics.add(r)

                elif tariff.id == 10:
                    date = timezone.now() + datetime.timedelta(days=day_and_prices.day)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=price, dead_time=date)
                    for r in t.get('rubrics'):
                        user_tariff_func.contact_rubric_list.add(r)
                    user_tariff_func.contact_rubric = True
                    user_tariff_func.contact_rubric_dead_time = date
                    user_tariff_func.vip_vacancy_count_rubrics += 1
                    user_tariff_func.vip_vacancy_deed_time = date
                    user_tariff_func.save()

                elif tariff.id == 11:
                    date = timezone.now() + datetime.timedelta(days=day_and_prices.day)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=price, dead_time=date)
                    user_tariff_func.contact_amount += 40
                    user_tariff_func.contact_amount_dead_time = date
                    user_tariff_func.vip_vacancy_count_rubrics += 3
                    user_tariff_func.vip_vacancy_deed_time = timezone.now() + datetime.timedelta(days=7)
                    user_tariff_func.save()

                elif tariff.id == 12:
                    date = timezone.now() + datetime.timedelta(days=day_and_prices.day)
                    MyTariff.objects.create(user=user, tariff=tariff.title, price=price, dead_time=date)
                    for r in t.get('rubrics'):
                        user_tariff_func.contact_rubric_list.add(r)
                    user_tariff_func.contact_rubric_dead_time = date
                    user_tariff_func.vip_vacancy_count_rubrics += 5
                    user_tariff_func.vip_vacancy_count_all_rubrics += 5
                    user_tariff_func.vip_vacancy_deed_time = timezone.now() + datetime.timedelta(days=7)
                    user_tariff_func.save()
            wallet.amount -= amount
            WalletHistory.objects.create(wallet=wallet, status='-', amount=amount, client=user.username)
            tariffs_title = []
            for d in tariffs:
                tariff = Tariff.objects.get(id=d.get('tariff'))
                tariffs_title.append(tariff.title)
            tariffs_title = ', '.join(tariffs_title)
            EntityAllHistory.objects.create(user=wallet.user, amount=amount,
                                            comment=tariffs_title,
                                            balance=wallet.amount)
            wallet.save()

            return Response({"detail": "Success!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)


class ReplenishmentTransaction(APIView):
    def post(self, request):
        payment = f'{request.user.username} - тестовый баланс'
        amount = request.data.get("amount")
        wallet_id = request.data.get("wallet")
        if amount and wallet_id:
            wallet = Wallet.objects.get(id=wallet_id)
            wallet.amount = wallet.amount + int(amount)
            WalletHistory.objects.create(wallet=wallet, status='+', amount=amount, comment=payment,
                                         client=wallet.user.entity_profile.company)
            EntityAllHistory.objects.create(user=wallet.user, amount=amount,
                                            comment=payment,
                                            balance=wallet.amount)
            wallet.save()
            delete_debtor(wallet, amount)
            pay_history(wallet, amount, payment)
            if wallet.user.entity_profile.manager.exists():
                plan_done(wallet.user.entity_profile.manager.first(), amount)
            return Response({"detail": "Success!"}, status=status.HTTP_200_OK)

        return Response({"error": "Amount or wallet required!"}, status=status.HTTP_400_BAD_REQUEST)



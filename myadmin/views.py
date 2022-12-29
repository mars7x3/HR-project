import datetime

from django.utils import timezone

from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.models import EntityProfile, PasswordTest
from accounts.utils import generate_pwd, send_new_pwd
from accounts.views import CustomView
from tariffs.models import UserTariffFunction, MyTariff, Tariff
from accounts.permissions import IsMainPermission
from accounts.serializers import EntityProfileSerializer, AdminManagerSerializer
from resume.models import Resume, Specialization
from resume.serializers import ResumeSerializer
from test_wallet.models import WalletHistory
from test_wallet.utils import check_amount
from vacancy.models import Vacancy
from vacancy.serializers import VacancySerializer
from .serializers import *
from .models import *
from .utils import plan_done, pay_history


class MyPaginationClass(PageNumberPagination):
    page_size = 40


class MainPlanView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        plans = Plan.objects.all()
        result = int()
        done = int()
        for p in plans:
            result += p.amount
            done += round(p.done / (result / 100))
        return Response({"data": {'result': result, 'done': done}}, status=status.HTTP_200_OK)


class PlanListView(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated, IsMainPermission]


class SelfUserView(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsMainPermission]


class PlanViewSet(SelfUserView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class PayHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        history = PayHistory.objects.all()
        amount = int()
        for h in history:
            amount += h.amount
        return Response({'amount': amount}, status=status.HTTP_200_OK)


class PayHistoryListView(viewsets.ReadOnlyModelViewSet):
    queryset = PayHistory.objects.all()
    serializer_class = PayHistorySerializer
    permission_classes = [IsAuthenticated, IsMainPermission]
    pagination_class = MyPaginationClass


class TermsView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        terms = TermsHistory.objects.filter(status='None').count()
        return Response({'terms': terms}, status=status.HTTP_200_OK)


class TermsListView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        terms = TermsHistory.objects.all()
        serializer = TermsHistorySerializer(terms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TermsViewSet(CustomView):
    queryset = TermsHistory.objects.all()
    serializer_class = TermsHistorySerializer
    permission_classes = [IsAuthenticated, IsMainPermission]


class LimitsView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        limits = LimitsHistory.objects.filter(status='None').count()
        return Response({'limits': limits}, status=status.HTTP_200_OK)


class LimitsListView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        limits = LimitsHistory.objects.all()
        serializer = LimitsHistorySerializer(limits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LimitsViewSet(CustomView):
    queryset = LimitsHistory.objects.all()
    serializer_class = LimitsHistorySerializer
    permission_classes = [IsAuthenticated, IsMainPermission]


class LimitsCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        LimitsHistory.objects.create()
        return Response({"detail": "Success!"}, status=status.HTTP_200_OK)


class DumpsView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        count = DumpsHistory.objects.all().count()
        new = DumpsHistory.objects.filter(status='None').count()
        amount = int()
        for d in DumpsHistory.objects.all():
            amount += d.last_transaction_amount
        return Response({'data': {'count': count, 'new': new, 'amount': amount}, }, status=status.HTTP_200_OK)


class DumpsListView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        dumps = DumpsHistory.objects.all()
        serializer = DumpsHistorySerializer(dumps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DumpsViewSet(SelfUserView):
    queryset = DumpsHistory.objects.all()
    serializer_class = DumpsHistorySerializer


class DebtorsView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        debtors = Debtors.objects.all()
        count = debtors.count()
        amount = int()
        for d in debtors:
            amount += d.transaction_amount

        return Response({'data': {'amount': amount, 'company': count}}, status=status.HTTP_200_OK)


class DebtorsListView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        dumps = Debtors.objects.all()
        serializer = DebtorsSerializer(dumps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DebtorsViewSet(SelfUserView):
    queryset = Debtors.objects.all()
    serializer_class = DebtorsSerializer


class CompanyListView(viewsets.ReadOnlyModelViewSet):
    queryset = EntityProfile.objects.filter(is_moderation=True)
    permission_classes = [IsAuthenticated, IsMainPermission]
    serializer_class = EntityProfileSerializer
    pagination_class = MyPaginationClass

    @action(detail=False, methods=['get'])
    def search(self, request, **kwargs):
        queryset = self.get_queryset()
        kwargs = {}

        manager = request.query_params.get('manager')
        if manager:
            manager = MyUser.objects.get(id=manager)
            queryset = manager.manager.profiles

        company = request.query_params.get('company')
        if company:
            kwargs['company__icontains'] = company

        username = request.query_params.get('username')
        if username:
            if MyUser.objects.filter(username=username):
                kwargs['user__id'] = MyUser.objects.get(username=username).id

        profiles = queryset.filter(**kwargs)

        page = self.paginate_queryset(profiles if profiles.exists() else queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class CompanyModerationListView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsMainPermission]
    pagination_class = MyPaginationClass
    queryset = EntityProfile.objects.filter(is_moderation=False)
    serializer_class = EntityProfileSerializer


class VacancyListView(viewsets.ReadOnlyModelViewSet):
    queryset = Vacancy.objects.filter(is_moderation=True)
    permission_classes = [IsAuthenticated, IsMainPermission]
    serializer_class = VacancySerializer
    pagination_class = MyPaginationClass

    # def get(self, request):
    #     profiles = Vacancy.objects.filter(is_moderation=True)
    #     serializer = VacancySerializer(profiles, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def search(self, request, **kwargs):
        queryset = self.get_queryset()
        kwargs = {}

        position = request.query_params.get('position')
        if position:
            kwargs['position__icontains'] = position

        is_active = request.query_params.get('active')
        if is_active:
            if int(is_active) == 1:
                kwargs['is_active'] = True
            if int(is_active) == 0:
                kwargs['is_active'] = False

        company = request.query_params.get('company')
        if company:
            user = MyUser.objects.get(username=company).id
            kwargs['user'] = user

        vacancies = queryset.filter(**kwargs)
        page = self.paginate_queryset(vacancies if vacancies.exists() else queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class VacancyModerationListView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsMainPermission]
    queryset = Vacancy.objects.filter(is_moderation=False)
    serializer_class = VacancySerializer
    pagination_class = MyPaginationClass


class ResumeListView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsMainPermission]
    queryset = Resume.objects.filter(is_moderation=True)
    serializer_class = AdminResumeSerializer
    pagination_class = MyPaginationClass

    @action(detail=False, methods=['get'])
    def search(self, request, **kwargs):
        queryset = self.get_queryset()
        kwargs = {}

        position = request.query_params.get('position')
        if position:
            kwargs['position__icontains'] = position

        is_active = request.query_params.get('active')
        if is_active:
            if int(is_active) == 1:
                kwargs['is_active'] = True
            if int(is_active) == 0:
                kwargs['is_active'] = False

        email = request.query_params.get('company')
        if email:
            queryset = MyUser.objects.get(email=email).resume.all()

        resumes = queryset.filter(**kwargs)
        page = self.paginate_queryset(resumes if resumes.exists() else queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ResumeModerationListView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsMainPermission]
    queryset = Resume.objects.filter(is_moderation=False)
    serializer_class = AdminResumeSerializer
    pagination_class = MyPaginationClass


class BannerView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsMainPermission]
    queryset = UserTariffFunction.objects.filter(banner=True)
    serializer_class = BannerSerializer


class EmployerView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsMainPermission]
    queryset = UserTariffFunction.objects.filter(employer=True)
    serializer_class = EmployerSerializer


class AdminPurchaseTransaction(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def post(self, request):
        tariffs = request.data.get("tariffs")
        user = MyUser.objects.get(id=request.data.get('user'))
        wallet = user.wallet

        amount = check_amount(tariffs)

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
                date = datetime.datetime(2100, 1, 1, 12, 00, 00)
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
                                        comment=f"{request.user.username} / {tariffs_title}",
                                        balance=wallet.amount)
        wallet.save()
        if wallet.amount < 0:
            user.debtors.first().delete()
            Debtors.objects.create(company=user, manager=user.entity_profile.manager.first(),
                                   transaction_amount=wallet.amount)

        return Response({"detail": "Success!"}, status=status.HTTP_200_OK)


class AdminReplenishmentTransaction(APIView):
    def post(self, request):
        payment = f'{request.user.username} - внутреннее пополнение'
        amount = request.data.get("amount")
        wallet_id = request.data.get("wallet")
        comment = request.data.get('comment')
        if amount and wallet_id:
            wallet = Wallet.objects.get(id=wallet_id)
            wallet.amount = wallet.amount + int(amount)
            WalletHistory.objects.create(wallet=wallet, status='+', amount=amount, comment=comment,
                                         client=wallet.user.entity_profile.company)
            EntityAllHistory.objects.create(user=wallet.user, amount=amount,
                                            comment=f"{payment} / {comment}", balance=wallet.amount)
            wallet.save()
            pay_history(wallet, amount, payment, comment)
            if wallet.user.entity_profile.manager.exists():
                plan_done(wallet.user.entity_profile.manager.first(), amount)

            return Response({"detail": "Success!"}, status=status.HTTP_200_OK)

        return Response({"error": "Amount or wallet required!"}, status=status.HTTP_400_BAD_REQUEST)


class ManagersListView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        manager = Manager.objects.all()
        serializer = AdminManagerSerializer(manager, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManagerUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def post(self, request):
        manager = Manager.objects.get(id=request.data.get('manager'))
        profile = EntityProfile.objects.get(id=request.data.get('profile'))
        if profile.manager.exists():
            profiles = Manager.objects.filter(profiles=profile).first()
            profiles.profiles.remove(profile)
            profiles.save()
        manager.profiles.add(profile)
        manager.save()

        return Response({"detail": "Success!"}, status=status.HTTP_200_OK)


class CallRequestView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        call_request = CallRequest.objects.all()
        serializer = CallRequestSerializer(call_request, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CallRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try: phone = request.data.get('phone')
        except: pass
        CallRequest.objects.create(company=user, manager=user.entity_profile.manager.first(),
                                   status='new', phone=phone)
        return Response({"detail": "Success!"}, status=status.HTTP_200_OK)


class CallRequestUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def post(self, request):
        call_request = request.data.get('call_request')
        comment = request.data.get('comment')
        call_request = CallRequest.objects.get(id=call_request)
        call_request.status = 'Обработано'
        call_request.comment = comment
        call_request.save()
        return Response({"detail": "Success!"}, status=status.HTTP_200_OK)


class CheckView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        tariffs = MyTariff.objects.filter(is_terms=False)
        for t in tariffs:
            if t.dead_time <= timezone.now() + datetime.timedelta(days=3):
                TermsHistory.objects.create(company=t.user, manager=t.user.entity_profile.manager.first(),
                                            tariff=t.tariff, tariff_price=t.price, tariff_dead_time=t.dead_time)
                print(t)
                t.is_terms = True
                t.save()

        wallets = WalletHistory.objects.filter(status='+', is_dumps=False)
        for t in wallets:
            if t.created_at <= timezone.now() - datetime.timedelta(days=2):
                DumpsHistory.objects.create(company=t.wallet.user, manager=t.wallet.user.entity_profile.manager.first(),
                                            last_transaction=t.created_at, last_transaction_amount=t.amount)
                t.is_dumps = True
                t.save()

        return Response({"detail": "Success!"}, status=status.HTTP_200_OK)


class DownPwdView(APIView):
    permission_classes = [IsMainPermission]

    def post(self, request):
        user_id = request.data.get('user')
        user = MyUser.objects.get(id=user_id)
        pwd = generate_pwd()
        user.set_password(pwd)
        user.save()
        PasswordTest.objects.create(username=user.username, password=pwd)
        send_new_pwd(pwd, user.email)
        return Response({'detail': "Успешный сброс пароля."}, status=status.HTTP_200_OK)


# class ActiveCodeListView(APIView):
#     permission_classes = [IsMainPermission]
#
#     def get(self, request):
#         codes = EmailAndCode.objects.all()
#         serializer = ActiveCodeSerializer(codes, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)




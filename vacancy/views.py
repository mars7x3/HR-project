from datetime import timedelta

from django.utils import timezone
from django.utils.timezone import localtime
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAuthorPermission, IsEntityAuthenticated, PostingUserIsAuthorPermission
from accounts.utils import send_postings
from resume.models import Resume
from .models import Vacancy, Postings, ApplicantFavorite
from vacancy.serializers import VacancySerializer, PostingsSerializer


class MyPaginationClass(PageNumberPagination):
    page_size = 40


class VacancyCustomView(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]


class SelfUserView(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAuthorPermission]


class VacancyViewSet(SelfUserView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer


class VacancyListView(viewsets.ReadOnlyModelViewSet):
    queryset = Vacancy.objects.filter(vip_status=False, is_active=True, archive=False)
    serializer_class = VacancySerializer
    pagination_class = MyPaginationClass

    @action(detail=False, methods=['get'])
    def search(self, request, **kwargs):
        queryset = self.get_queryset()
        vacancies = queryset
        kwargs = {}
        order_by_kwargs = set()

        city = request.query_params.get('city')
        if city:
            kwargs['city__in'] = city.split('$')

        time = request.query_params.get('time')
        if time:
            kwargs['created_at__gte'] = timezone.now() - timezone.now()(hours=int(time))

        position = request.query_params.get('position')
        if position:
            kwargs['position__icontains'] = position

        salary = request.query_params.get('salary')
        if salary:
            kwargs['salary__lte'] = salary
            order_by_kwargs.add("-salary")

        exp = request.query_params.get('exp')
        if exp:
            kwargs['experience'] = exp

        schedule = request.query_params.get('schedule')
        if schedule:
            kwargs['schedule'] = schedule

        edu = request.query_params.get('edu')
        if edu:
            kwargs['education'] = edu

        group = request.query_params.get('group')
        if group:
            kwargs['group'] = group

        vacancies = vacancies.filter(**kwargs)
        if order_by_kwargs:
            vacancies = vacancies.order_by(*order_by_kwargs)

        # serializer = VacancySerializer(vacancies if vacancies.exists() else queryset, many=True)
        #
        # return Response(serializer.data)
        page = self.paginate_queryset(vacancies if vacancies.exists() else queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class VacancyONEView(viewsets.ReadOnlyModelViewSet):
    # По id получаем резюме вне зависимости от статусов
    queryset = Vacancy.objects.filter(is_moderation=True)
    serializer_class = VacancySerializer


class VIPVacancyListView(generics.ListAPIView):
    queryset = Vacancy.objects.filter(vip_status=True, is_active=True, archive=False)
    serializer_class = VacancySerializer


class VacancySpecListView(APIView):
    pagination_class = MyPaginationClass

    def post(self, request):
        data = Vacancy.objects.filter(specialization=request.data.get('spec_slug'), vip_status=False, is_active=True,
                                      archive=False)
        serializer = VacancySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostingsUpdateView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Postings.objects.all()
    serializer_class = PostingsSerializer
    permission_classes = [IsEntityAuthenticated, PostingUserIsAuthorPermission]


class PostingsApplicantIsView(APIView):
    permission_classes = [IsAuthenticated, PostingUserIsAuthorPermission]

    def post(self, request):
        try:
            posting = request.data.get('id')
            posting = Postings.objects.get(id=posting)
            posting.applicant_is_viewed = True
            posting.save()
            return Response({'detail': 'Success.'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Что-то пошло не так!'}, status=status.HTTP_400_BAD_REQUEST)


class PostingsCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resume_id, vacancy_id = request.data.get('resume'), request.data.get('vacancy')

        if not resume_id or not vacancy_id:
            return Response({"error": "Что-то пошло не так!"}, status=status.HTTP_400_BAD_REQUEST)

        if Resume.objects.get(id=resume_id).user != request.user:
            return Response({"error": "Это не ваше резюме!"}, status=status.HTTP_400_BAD_REQUEST)

        postings = Postings.objects.filter(resume__id=resume_id, vacancy__id=vacancy_id).exists()
        if postings:
            return Response({'error': 'Вы уже откликались за эту вакансию!'}, status=status.HTTP_400_BAD_REQUEST)

        posting = Postings.objects.create(resume_id=resume_id, vacancy_id=vacancy_id, text=request.data.get('text'))
        send_postings(posting)

        return Response({'detail': 'Вы откликнулись на вакансию!'}, status=status.HTTP_200_OK)


class ApplicantFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        vacancy = request.data.get('vacancy')
        if vacancy:
            favorite, _ = ApplicantFavorite.objects.get_or_create(user=user, vacancy_id=vacancy)
            if favorite.favorite is False:
                favorite.favorite = True
                favorite.save()
            else:
                favorite.delete()
            return Response({"detail": "Success."}, status=status.HTTP_200_OK)
        return Response({"error": "Vacancy is required!"}, status=status.HTTP_400_BAD_REQUEST)


class VacancyUpTime(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            vacancy = Vacancy.objects.get(id=request.data.get('vacancy'))
            if timezone.now() < vacancy.up_time + timedelta(minutes=1):
                return Response({"error": f"Вы сможете обновить после {localtime(timedelta(minutes=1) + vacancy.up_time).strftime('%H:%M-%d.%m')}"},
                                status=status.HTTP_400_BAD_REQUEST)
            vacancy.up_time = timezone.now()
            vacancy.save()
            return Response({"detail": "Успешное обновление!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print("[Warning] - VacancyUpTime /// " + str(e))
            return Response({"error": "Что-то пошло не так!"}, status=status.HTTP_400_BAD_REQUEST)




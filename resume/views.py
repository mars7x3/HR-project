import xlsxwriter

from django.utils import timezone
from datetime import timedelta, date

from django.utils.timezone import localtime
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAuthorPermission
from .models import Resume, Specialization, Positions
from .serializers import *


class MyPaginationClass(PageNumberPagination):
    page_size = 40
    page_size_query_param = 'pagesize'
    max_page_size = 100


class SpecializationListView(generics.ListAPIView):
    queryset = Specialization.objects.filter(parent_specialization=None)
    serializer_class = SpecializationSerializer


class SubSpecializationListView(APIView):
    def post(self, request):
        data = Specialization.objects.filter(parent_specialization=request.data.get('spec_slug'))
        serializer = SpecializationSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResumeSpecListView(APIView):
    pagination_class = MyPaginationClass

    def post(self, request):
        data = Resume.objects.filter(specialization=request.data.get('spec_slug'), vip_status=False, is_active=True,
                                     status_is_hidden=False)

        serializer = ResumeSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SelfUserView(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAuthorPermission]


class ResumeViewSet(SelfUserView):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer


class ResumeTagStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAuthorPermission]

    def post(self, request):
        try:
            data = request.data.get('tag')
            resume = Resume.objects.get(id=request.data.get('resume'))
            if int(data) == 0:
                resume.status_is_hidden = True
                resume.status_is_view_all = False
                resume.status_active_search = False
                resume.status_variant_view = False
                resume.save()
            if int(data) == 1:
                resume.status_is_hidden = False
                resume.status_is_view_all = True
                resume.status_active_search = False
                resume.status_variant_view = False
                resume.save()
            if int(data) == 2:
                resume.status_is_hidden = False
                resume.status_is_view_all = False
                resume.status_active_search = True
                resume.status_variant_view = False
                resume.save()
            if int(data) == 3:
                resume.status_is_hidden = False
                resume.status_is_view_all = False
                resume.status_active_search = False
                resume.status_variant_view = True
                resume.save()
            return Response({"detail": "Success!"}, status=status.HTTP_200_OK)

        except:
            return Response({"error": "ERROR!"}, status=status.HTTP_400_BAD_REQUEST)


class ResumeListView(viewsets.ReadOnlyModelViewSet):
    queryset = Resume.objects.filter(vip_status=False, is_active=True, status_is_hidden=False)
    serializer_class = ResumeSerializer
    pagination_class = MyPaginationClass

    @action(detail=False, methods=['get'])
    def search(self, request, **kwargs):
        queryset = self.get_queryset()
        resumes = queryset
        kwargs = {}
        order_by_kwargs = set()

        position = request.query_params.get('position')
        if position:
            kwargs['position__icontains'] = position

        city = request.query_params.get('city')
        if city:
            kwargs['city_for_work__in'] = city.split('$')

        time = request.query_params.get('time')
        if time:
            kwargs['created_at__gte'] = timezone.now() - timedelta(hours=int(time))

        salary = request.query_params.get('salary')
        if salary:
            kwargs['salary__lte'] = salary
            order_by_kwargs.add("-salary")

        exp = request.query_params.get('exp')
        if exp:
            kwargs['experience'] = exp

        schedule = request.query_params.get('schedule')
        if schedule:
            kwargs['type_of_employment'] = schedule

        agge = request.query_params.get('agge')
        if agge:
            start_age = agge.split('$')[0]
            end_age = agge.split('$')[1]
            resumes = resumes.filter(agge__gte=start_age)
            resumes = resumes.filter(agge__lte=end_age)

        gender = request.query_params.get('gender')
        if gender:
            kwargs['gender'] = gender

        driver_license = request.query_params.get('driver_license')
        if driver_license:
            kwargs['driver_license__in'] = driver_license.split('$')

        edu = request.query_params.get('edu')
        if edu:
            kwargs['education'] = edu

        language = request.query_params.get('language')
        if language:
            kwargs['languages__icontains'] = language.split('$')

        resumes = resumes.filter(**kwargs)
        if order_by_kwargs:
            resumes = resumes.order_by(*order_by_kwargs)

        # serializer = ResumeSerializer(resumes if resumes.exists() else queryset, many=True)
        #
        # return Response(serializer.data)

        page = self.paginate_queryset(resumes if resumes.exists() else queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ResumeONEView(viewsets.ReadOnlyModelViewSet):
    #По id получаем резюме вне зависимости от статусов
    queryset = Resume.objects.filter(is_moderation=True)
    serializer_class = ResumeSerializer


class VIPResumeListView(generics.ListAPIView):
    queryset = Resume.objects.filter(vip_status=True, is_active=True)
    serializer_class = ResumeSerializer


class PositionsListView(APIView):
    def get(self, request):
        data = Positions.objects.all()
        serializer = PositionsSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResumeUpTime(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            resume = Resume.objects.get(id=request.data.get('resume'))
            if timezone.now() - timedelta(minutes=1) <= resume.up_time:
                return Response({"error": f"Вы сможете обновить после {localtime(timedelta(minutes=1) + resume.up_time).strftime('%H:%M-%d.%m')}"},
                                status=status.HTTP_400_BAD_REQUEST)

            resume.up_time = timezone.now()
            resume.save()
            return Response({"detail": "Успешное обновление!"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Что-то пошло не так!"}, status=status.HTTP_400_BAD_REQUEST)


class EntityFavoriteView(APIView):
    def post(self, request):
        user = request.user
        resume = request.data.get('resume')
        if resume:
            favorite, _ = EntityFavorite.objects.get_or_create(user=user, resume_id=resume)
            if favorite.favorite is False:
                favorite.favorite = True
                favorite.save()
            else:
                favorite.delete()
            return Response({"detail": "Success."}, status=status.HTTP_200_OK)
        return Response({"error": "Resume is required!"}, status=status.HTTP_400_BAD_REQUEST)


class CVViewView(APIView):

    def get(self, request):
        ccview_id = request.data.get('ccview_id')
        ccview = CVView.objects.get(id=ccview_id)
        ccview.is_viewed = True
        ccview.is_new = False
        ccview.save()
        return Response({"data": "Success!"}, status=status.HTTP_200_OK)

    def post(self, request):
        resume = request.data.get('resume_id')
        company = request.user
        ccviews = CVView.objects.filter(company=company, resume__id=resume).first()
        if ccviews:
            ccviews.is_new = True
            ccviews.is_viewed = False
            ccviews.created_at = timezone.now()
            ccviews.save()
            return Response({"data": "Success!"}, status=status.HTTP_200_OK)

        CVView.objects.create(resume=Resume.objects.get(id=resume), company=MyUser.objects.get(id=company))
        return Response({"data": "Success!"}, status=status.HTTP_200_OK)


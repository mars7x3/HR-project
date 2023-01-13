from rest_framework.response import Response

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from resume.serializers import ResumePhoneSerializer
from .models import *
from .serializers import *
from .utils import check_dead_time_tariff


class ResumePBPView(APIView):
    """Резюме поштучно"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resume = Resume.objects.get(id=request.data.get('resume'))
        user = request.user
        user_tariff = user.user_tariff_function
        check_dead_time_tariff(user)
        if user.access_to_resumes.all().filter(user=user, resume=resume):
            serializer = ResumePhoneSerializer(resume)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif user_tariff.contact_amount > 0:
            user_tariff.contact_amount -= 1
            user_tariff.save()
            serializer = ResumePhoneSerializer(resume)
            if not user.access_to_resumes.all().filter(resume=resume):
                AccessToResume.objects.create(user=user, resume=resume)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Вам необходимо купить тариф!"}, status=status.HTTP_400_BAD_REQUEST)


class ResumeRubricView(APIView):
    """Резюме в рубрике"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resume = Resume.objects.get(id=request.data.get('resume'))
        user = request.user
        user_tariff = user.user_tariff_function
        for r in user_tariff.contact_rubric_list.all():
            if r in resume.specialization.all() and user_tariff.contact_rubric:
                user_tariff.contact_amount -= 1
                user_tariff.save()
                phones = resume.phones.all()
                serializer = ResumePhoneSerializer(phones, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Вам необходимо купить тариф!"}, status=status.HTTP_400_BAD_REQUEST)


class ResumeAllView(APIView):
    """Резюме все"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resume = Resume.objects.get(id=request.data.get('resume'))
        user = request.user
        user_tariff = user.user_tariff_function
        if user_tariff.contact_rubric:
            user_tariff.contact_amount -= 1
            user_tariff.save()
            phones = resume.phones.all()
            serializer = ResumePhoneSerializer(phones, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Вам необходимо купить тариф!"}, status=status.HTTP_400_BAD_REQUEST)


class MyTariffListView(APIView):
    def get(self, request):
        queryset = request.user.my_tariffs.all()
        serializer = MyTariffSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllTariffsView(APIView):
    def get(self, request):
        tariffs = PriceList.objects.all()
        serializer = PriceListSerializer(tariffs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployerListViewL(viewsets.ReadOnlyModelViewSet):
    queryset = UserTariffFunction.objects.filter(employer_is_active=True)
    serializer_class = EmployerListSerializer


class BannerListViewL(viewsets.ReadOnlyModelViewSet):
    queryset = UserTariffFunction.objects.filter(banner_is_active=True)
    serializer_class = BannerListSerializer



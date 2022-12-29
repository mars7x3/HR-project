from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('active-employers', EmployerListViewL)
router.register('active-banners', BannerListViewL)

urlpatterns = [
    path('mytariffs/', MyTariffListView.as_view()),
    path('alltariffs/', AllTariffsView.as_view()),
    path('get-contacts/pbp/', ResumePBPView.as_view()),
    path('get-contacts/rubric/', ResumeRubricView.as_view()),

    path('', include(router.urls)),

]

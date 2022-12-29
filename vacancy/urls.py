from django.urls import path, include
from rest_framework.routers import DefaultRouter

from resume.views import ResumeSpecListView
from .views import *

router = DefaultRouter()
router.register('vacancies', VacancyListView)
router.register('vacancy', VacancyViewSet)
router.register('vacancy-one', VacancyONEView)
router.register('postings/update', PostingsUpdateView)

urlpatterns = [
    path('category/vacancies/', VacancySpecListView.as_view()),

    path('vacancy-uptime/', VacancyUpTime.as_view()),

    path('vacancies/vip/', VIPVacancyListView.as_view()),
    path('postings/create/', PostingsCreateView.as_view()),
    path('postings/is-viewed/', PostingsApplicantIsView.as_view()),


    path('favorite/entity/', ApplicantFavoriteView.as_view()),

    path('', include(router.urls)),

]

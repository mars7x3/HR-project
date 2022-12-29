from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import *

router = DefaultRouter()
router.register('resumes', ResumeListView)
router.register('resume', ResumeViewSet)
router.register('resume-one', ResumeONEView)


urlpatterns = [
    path('resume-status-patch/', ResumeTagStatusUpdateView.as_view()),

    path('category/', SpecializationListView.as_view()),
    path('subcategory/', SubSpecializationListView.as_view()),

    path('category/resumes/', ResumeSpecListView.as_view()),
    path('resumes/vip/', VIPResumeListView.as_view()),
    path('positions/', PositionsListView.as_view()),

    path('ccviews/', CVViewView.as_view()),

    path('resume-uptime/', ResumeUpTime.as_view()),
    path('favorite/applicant/', EntityFavoriteView.as_view()),

    path('', include(router.urls)),

]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import *

router = DefaultRouter()
router.register('entity/profiles', EntityProfileListView, basename='read_entity')
router.register('entity/profile', EntityProfileViewSet)
router.register('entity/personals', EntityPersonalListView, basename='read_personal')
router.register('entity/personal', EntityPersonalViewSet, basename='cud_personal')
router.register('profile/comments', ProfileCommentView)


urlpatterns = [
    path('me-info/entity/', EntityUserInfoView.as_view({'get': 'list'})),
    path('me-info/applicant/', ApplicantUserInfoView.as_view({'get': 'list'})),
    path('applicant/image/', ApplicantImageView.as_view()),
    path('profile/requisite-delete/', EntityRequisiteDeleteView.as_view()),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('user/check-mail/', VerificationCodeView.as_view()),
    # path('user/check-code/', CheckEmailView.as_view()),
    path('user/register/', RegisterView.as_view()),
    path('user/delete/', DeleteView.as_view()),

    path('user/change-email/', ChangeEmailView.as_view()),

    path('user/change-pwd/', ChangePwdView.as_view()),
    path('user/forgot-pwd-verify/', VerifyForgotPwdView.as_view()),
    path('user/forgot-pwd/', ForgotPwdView.as_view()),

    path('profile/image/', ProfileImageView.as_view()),
    path('profile/image-update/', ProfileImageUpdateView.as_view()),

    path('myadmin/personal-list/', HRGroupPersonalListView.as_view()),
    path('myadmin/personal-delete/', HRGroupPersonalDeleteView.as_view()),
    path('myadmin/personal-update/', HRGroupPersonalUpdateView.as_view()),

    path('myadmin/checkuser/', CheckNoStatusUserView.as_view()),



    path('', include(router.urls)),


]

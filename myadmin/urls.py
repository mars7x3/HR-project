from django.urls import path, include

from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('myadmin/pay-list', PayHistoryListView, basename='pay-list')
router.register('myadmin/plan-list', PlanListView, basename='plan-list')
router.register('myadmin/plan-crud', PlanViewSet)
router.register('myadmin/terms-crud', TermsViewSet)
router.register('myadmin/limits-crud', LimitsViewSet)
router.register('myadmin/dumps-crud', DumpsViewSet)
router.register('myadmin/debtors-crud', DebtorsViewSet)

router.register('myadmin/companies', CompanyListView)
router.register('myadmin/companies-moderation', CompanyModerationListView)
router.register('myadmin/resumes', ResumeListView)
router.register('myadmin/resumes-moderation', ResumeModerationListView)
router.register('myadmin/vacancies', VacancyListView)
router.register('myadmin/vacancies-moderation', VacancyModerationListView)

router.register('myadmin/banner', BannerView)
router.register('myadmin/employer', EmployerView)

urlpatterns = [
    path('myadmin/plan/', MainPlanView.as_view()),
    path('myadmin/pay-history/', PayHistoryView.as_view()),
    path('myadmin/terms/', TermsView.as_view()),
    path('myadmin/terms-list/', TermsListView.as_view()),
    path('myadmin/limits/', LimitsView.as_view()),
    path('myadmin/limits-list/', LimitsListView.as_view()),
    path('myadmin/limits-create/', LimitsCreateView.as_view()),

    path('myadmin/dumps/', DumpsView.as_view()),
    path('myadmin/dumps-list/', DumpsListView.as_view()),
    path('myadmin/debtors/', DebtorsView.as_view()),
    path('myadmin/debtors-list/', DebtorsListView.as_view()),

    path('myadmin/transaction-minus/', AdminPurchaseTransaction.as_view()),
    path('myadmin/transaction-plus/', AdminReplenishmentTransaction.as_view()),
    path('myadmin/transaction-refund/', Refund.as_view()),


    path('myadmin/manager-list/', ManagersListView.as_view()),

    path('myadmin/call-request/', CallRequestView.as_view()),
    path('call-request-create/', CallRequestCreateView.as_view()),
    path('myadmin/call-request-update/', CallRequestUpdateView.as_view()),

    path('myadmin/check-view/', CheckView.as_view()),
    path('myadmin/manager-update/', ManagerUpdateView.as_view()),
    path('myadmin/manager-custom-list/', ManagerCustomListView.as_view()),


    path('myadmin/down-pwd-user/', DownPwdView.as_view()),
    # path('myadmin/active-code/', ActiveCodeListView.as_view()),

    path('', include(router.urls)),
]

from django.urls import path, include

from .views import *


urlpatterns = [
    path('create-pay-url/', CreatePayUrl.as_view()),
    path('check-transaction/', CheckTransactionView.as_view()),
    path('elsom-response/', ElsomResponseTransactionView.as_view()),

]

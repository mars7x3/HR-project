from django.urls import path, include

from .views import *


urlpatterns = [
    path('payment/paybox/create/', PayBoxCreateView.as_view()),
    path('payment/paybox/result/', PayBoxResultView.as_view()),


]

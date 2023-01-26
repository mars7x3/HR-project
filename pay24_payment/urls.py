from django.urls import path, include

from .views import *


urlpatterns = [
    path('payment/pay24/', Pay24View.as_view()),

]

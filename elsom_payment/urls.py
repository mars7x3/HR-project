from django.urls import path, include

from .views import *


urlpatterns = [
    path('payment/elsom/create/', ElsomCreateView.as_view()),
    path('payment/elsom/result/', ElsomResponseView.as_view()),

]

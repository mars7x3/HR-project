from django.urls import path, include
from .views import *


urlpatterns = [
    path('wallet/', WalletListView.as_view()),
    path('transaction/minus/', PurchaseTransaction.as_view()),
    path('transaction/plus/', ReplenishmentTransaction.as_view()),

]
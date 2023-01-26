import requests

from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from elsom_payment.models import TransactionReceipt
from elsom_payment.utils import elsom_payment_create, elsom_transaction_plus


class ElsomCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone, amount = request.data.get('phone'), request.data.get('amount')
        wallet = request.user.username

        if phone and amount:
            receipt = TransactionReceipt.objects.create(wallet=wallet, user_phone=phone, amount=amount)
            response = elsom_payment_create(receipt).get('Response').get('Result').get('URL')
            return Response({"elsom_url": response}, status=status.HTTP_200_OK)

        return Response({"error": "Введите пожалуйста номер телефона и сумму!"}, status=status.HTTP_400_BAD_REQUEST)


class ElsomResponseView(APIView):
    def post(self, request):
        response = request.data.get('PartnerPaymentResult')
        receipt = TransactionReceipt.objects.get(id=response.get('PartnerTrnID'))
        receipt.status = response.get('PaymentStatus')
        receipt.message = response.get('Message')
        receipt.save()
        if receipt.status == '1':
            elsom_transaction_plus(receipt)
        return Response({"Response": {"ErrorCode": "0", "ErrorMsg": "Success"}}, status=status.HTTP_200_OK)






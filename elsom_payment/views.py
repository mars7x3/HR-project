from django.utils import timezone
from datetime import timedelta

from django.shortcuts import render
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from elsom_payment.models import TransactionReceipt, TransactionID, CheckTransaction


class CreatePayUrl(APIView):

    def post(self, request):
        user_phone = request.data.get('phone')
        amount = request.data.get('amount')
        transaction_receipt = TransactionReceipt.objects.create(wallet=request.user.username, user_phone=user_phone,
                                                                amount=amount)
        transaction_id = TransactionID.objects.create(transaction_receipt=transaction_receipt)

        payload = {
            "CultureInfo": "ru-RU",
            "MSISDN": transaction_receipt.user_phone,
            "PmSISDN": "0501121551",
            "PartnerCode": "62952",
            "Password": "hr123456!",
            "ChequeNo": transaction_receipt.id,
            "PartnerTrnID": transaction_id.id,
            "Amount": transaction_receipt.amount,
            "CashierNo": transaction_receipt.cashier_no,
        }
        url = 'elsom_create_url'
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)
        if response[0] == 'success':
            CheckTransaction.objects.create(transaction_receipt=transaction_receipt)
            return Response({"elsom_response": response[1]}, status=status.HTTP_200_OK)
        if response[0] != 'success':
            return Response({"elsom_response": response[1]}, status=status.HTTP_200_OK)
        transaction_receipt.delete()
        return Response({"error": "Ошибка создания URL платежа"}, status=status.HTTP_400_BAD_REQUEST)


class CheckTransactionView(APIView):
    def get(self, request):
        check_transaction = CheckTransaction.objects.all()

        for check in check_transaction:
            transaction_receipt = check.transaction_receipt
            transaction_id = transaction_receipt.transaction_ids.first()
            payload = {
                "CultureInfo": "ru-RU",
                "MSISDN": transaction_receipt.user_phone,
                "Password": "hr123456!",
                "PartnerTrnID": transaction_id.id,
            }
            url = 'elsom_check_status_url'
            headers = {}

            if check.created_at < timezone.now() - timedelta(seconds=15):
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.get('Response').get('Result').get('PaymentStatus') == 'A':
                    check.delete()
                    transaction_receipt.status = 'платеж прошел успешно'
                    transaction_receipt.save()
                if response.get('Response').get('Result').get('PaymentStatus') == '1':
                    transaction_receipt.status = 'платеж в обработке'
                    transaction_receipt.save()
                if response.get('Response').get('Result').get('PaymentStatus') == '2':
                    check.delete()
                    transaction_receipt.status = 'Не успешно время транзакции вышла'
                    transaction_receipt.save()
                if response.get('Response').get('Result').get('PaymentStatus') == '3':
                    check.delete()
                    transaction_receipt.status = 'платеж отменен партнером'
                    transaction_receipt.save()
                if response.get('Response').get('Result').get('PaymentStatus') == '4':
                    check.delete()
                    transaction_receipt.status = 'другая ошибка'
                    transaction_receipt.save()

        return Response({"detail": "Success!"}, status=status.HTTP_200_OK)


class ElsomResponseTransactionView(APIView):
    def post(self, request):
        transaction_receipt = TransactionID.objects.get(id=request.data.get('PartnerTrnID')).transaction_receipt
        elsom_response = request.data.get('PaymentStatus')
        if elsom_response == 'A':
            transaction_receipt.transaction_check.delete()
            transaction_receipt.status = 'платеж прошел успешно'
            transaction_receipt.save()
            return Response({"Response": {"ErrorCode": "0", "ErrorMsg": "Success"}}, status=status.HTTP_200_OK)
        if elsom_response == '1':
            transaction_receipt.status = 'платеж в обработке'
            transaction_receipt.save()
            return Response({"Response": {"ErrorCode": "0", "ErrorMsg": "Success"}}, status=status.HTTP_200_OK)
        if elsom_response == '2':
            transaction_receipt.transaction_check.delete()
            transaction_receipt.status = 'Не успешно время транзакции вышла'
            transaction_receipt.save()
            return Response({"Response": {"ErrorCode": "0", "ErrorMsg": "Success"}}, status=status.HTTP_200_OK)
        if elsom_response == '3':
            transaction_receipt.transaction_check.delete()
            transaction_receipt.status = 'платеж отменен партнером'
            transaction_receipt.save()
            return Response({"Response": {"ErrorCode": "0", "ErrorMsg": "Success"}}, status=status.HTTP_200_OK)
        if elsom_response == '4':
            transaction_receipt.transaction_check.delete()
            transaction_receipt.status = 'другая ошибка'
            transaction_receipt.save()
            return Response({"Response": {"ErrorCode": "0", "ErrorMsg": "Success"}}, status=status.HTTP_200_OK)







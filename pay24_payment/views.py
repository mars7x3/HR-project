from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from pay24_payment.utils import pay24_check_account, pay24_pay, pay24_check_pay_status


class Pay24View(APIView):

    def get(self, request):
        command = request.query_params.get('command')
        if command == 'check':
            account = request.query_params.get('account')
            result = pay24_check_account(account)
            return Response(result, status=status.HTTP_200_OK)

        elif command == 'pay':
            account = request.query_params.get('account')
            txn_id = request.query_params.get('txn_id')
            txn_date = request.query_params.get('txn_date')
            amount = request.query_params.get('sum')
            result = pay24_pay(account, txn_id, amount, txn_date)
            return Response(result, status=status.HTTP_200_OK)

        elif command == 'check_pay_status':
            txn_id = request.query_params.get('txn_id')
            result = pay24_check_pay_status(txn_id)
            return Response(result, status=status.HTTP_200_OK)



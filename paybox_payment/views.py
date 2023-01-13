from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import PayBoxTransactionReceipt
from .utils import paybox_transaction, result_xml_0, result_xml_1, paybox_transaction_plus


class PayBoxCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user
        order_id = PayBoxTransactionReceipt.objects.create(wallet=user.wallet, pg_amount=data.get('amount')).id
        result = paybox_transaction(str(order_id), data.get('amount'))

        return Response({'pay_url': result}, status=status.HTTP_200_OK)


class PayBoxResultView(APIView):

    def post(self, request):
        data = request.data
        pg_order_id = data.get('pg_order_id')
        receipt = PayBoxTransactionReceipt.objects.get(id=pg_order_id)

        for key, value in data.items():
            setattr(receipt, key, value[0])
        receipt.save()

        if receipt.pg_result == '1':
            paybox_transaction_plus(receipt)
            response = result_xml_1(data.get('pg_salt'), data.get('pg_sig'))
            return Response(response, status=status.HTTP_200_OK)

        response = result_xml_0(data.get('pg_salt'), data.get('pg_sig'))
        return Response(response, status=status.HTTP_200_OK)



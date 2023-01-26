import xmltodict
from django.db import transaction


from myadmin.models import EntityAllHistory
from myadmin.utils import delete_debtor, pay_history, plan_done
from .models import Pay24TransactionReceipt
from test_wallet.models import Wallet, WalletHistory


def transaction_plus(wallet, amount):
    payment = 'Pay24'
    if amount and wallet:
        wallet.amount += int(amount)
        WalletHistory.objects.create(wallet=wallet, status='+', amount=amount, comment=payment,
                                     client=wallet.user.entity_profile.company)
        EntityAllHistory.objects.create(user=wallet.user, amount=amount, comment=payment, balance=wallet.amount)
        wallet.save()
        delete_debtor(wallet, amount)
        pay_history(wallet, amount, payment, payment)
        if wallet.user.entity_profile.manager.exists():
            plan_done(wallet.user.entity_profile.manager.first(), amount)


def pay24_check_account(account):
    wallet = Wallet.objects.filter(user__username=account)
    if wallet:
        dict_data = {'response': {'result': 0, 'comment': ''}}
        result = xmltodict.unparse(dict_data)
        return result

    dict_data = {'response': {'result': 5, 'comment': ''}}
    result = xmltodict.unparse(dict_data)
    return result


def pay24_pay(account, txn_id, amount, txn_date):
    wallet = Wallet.objects.filter(user__username=account)
    amount = int(amount)
    if wallet:
        try:
            with transaction.atomic():
                dict_data = {'response': {'txn_id': txn_id, 'result': 0, 'comment': ''}}
                result = xmltodict.unparse(dict_data)
                Pay24TransactionReceipt.objects.create(wallet=account, txn_id=txn_id, amount=amount, txn_date=txn_date,
                                                       result='0')
                transaction_plus(wallet.first(), amount)

                return result
        except Exception as e:
            print(e)
            dict_data = {'response': {'txn_id': txn_id, 'result': 8, 'comment': ''}}
            result = xmltodict.unparse(dict_data)
            return result

    dict_data = {'response': {'txn_id': txn_id, 'result': 5, 'comment': ''}}
    result = xmltodict.unparse(dict_data)
    return result


def pay24_check_pay_status(txn_id):
    if Pay24TransactionReceipt.objects.filter(txn_id=txn_id).exists():
        dict_data = {'response': {'txn_id': txn_id, 'result': 0, 'comment': 'платеж успешно проведен'}}
        result = xmltodict.unparse(dict_data)
        return result

    dict_data = {'response': {'txn_id': txn_id, 'result': 300, 'comment': 'Нет транзакции с таким txn_id.'}}
    result = xmltodict.unparse(dict_data)
    return result




import requests
import hashlib

import xmltodict
from django.conf import settings

from myadmin.models import EntityAllHistory
from myadmin.utils import pay_history, plan_done, delete_debtor
from test_wallet.models import Wallet, WalletHistory

url = "https://api.freedompay.money/init_payment.php"


# payload = {
#     'pg_merchant_id': settings.PG_MERCHANT_ID,
#     'pg_description': 'Пополнение баланса через PayBox',
#     'pg_salt': 'HR Group',
#     'pg_currency': 'KGS',
        # 'pg_check_url': 'http://hrgroup.kg/check',
    # 'pg_result_url': 'https://hrgroup.kg/api/v1/payment/paybox/result/',
    # 'pg_request_method': 'POST',
    # 'pg_success_url': 'https://hrgroup.kg',
    # 'pg_failure_url': 'https://hrgroup.kg',
    # 'pg_success_url_method': 'GET',
    # 'pg_failure_url_method': 'GET',
        # 'pg_state_url': 'http://hrgroup.kg/state',
        # 'pg_state_url_method': 'GET',
        # 'pg_site_url': 'http://hrgroup.kg/return',
    # 'pg_payment_system': 'EPAYWEBKGS',
        # 'pg_lifetime': '86400',
        # 'pg_user_phone': '996554730944',
        # 'pg_user_contact_email': 'm.ysakov.jcc@gmail.com',
        # 'pg_user_ip': '127.0.0.1',
        # 'pg_postpone_payment': '0',
        # 'pg_language': 'ru',
        # 'pg_testing_mode': '1',
        # 'pg_user_id': '1',
        # 'pg_recurring_start': '1',
        # 'pg_recurring_lifetime': '156',

# }


def make_flat_params_array(data):
    flat_list = []
    for k, v in sorted(data.items()):
        flat_list.append(v)
    flat_list.insert(0, 'init_payment.php')
    flat_list.append(settings.SECRET_KEY)
    return flat_list


def hash_for(data):
    data = data.encode()
    md5 = hashlib.md5(data).hexdigest()
    return md5


def paybox_transaction(order_id, amount):
    payload = {'pg_merchant_id': settings.PG_MERCHANT_ID, 'pg_description': 'Пополнение баланса через PayBox',
               'pg_salt': 'HR Group', 'pg_currency': 'KGS',
               'pg_result_url': 'https://hrgroup.kg/api/v1/payment/paybox/result/', 'pg_request_method': 'POST',
               'pg_success_url': 'https://hrgroup.kg', 'pg_failure_url': 'https://hrgroup.kg',
               'pg_success_url_method': 'GET', 'pg_failure_url_method': 'GET', 'pg_order_id': order_id,
               'pg_amount': amount}

    payload['pg_sig'] = hash_for(';'.join(make_flat_params_array(payload)))

    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload)
    tree = xmltodict.parse(response.content)
    pay_url = tree.get('response').get('pg_redirect_url')

    return pay_url


def result_xml_1(pg_salt, pg_sig):
    dict_data = {'response': {'pg_status': 'ok', 'pg_description': 'Заказ оплачен', 'pg_salt': pg_salt,
                              'pg_sig': pg_sig}}
    result = xmltodict.unparse(dict_data)
    return result


def result_xml_0(pg_salt, pg_sig):
    dict_data = {'response': {'pg_status': 'rejected', 'pg_description': 'Платеж отменен', 'pg_salt': pg_salt,
                              'pg_sig': pg_sig}}
    result = xmltodict.unparse(dict_data)
    return result


def paybox_transaction_plus(receipt):
    payment = 'PayBox'
    amount = receipt.pg_amount
    wallet_id = receipt.wallet
    if amount and wallet_id:
        wallet = Wallet.objects.get(user__username=wallet_id)
        wallet.amount += int(amount)
        WalletHistory.objects.create(wallet=wallet, status='+', amount=amount, comment=payment,
                                     client=wallet.user.entity_profile.company)
        EntityAllHistory.objects.create(user=wallet.user, amount=amount, comment=payment, balance=wallet.amount)
        wallet.save()
        delete_debtor(wallet, amount)
        pay_history(wallet, amount, payment, payment)
        if wallet.user.entity_profile.manager.exists():
            plan_done(wallet.user.entity_profile.manager.first(), amount)


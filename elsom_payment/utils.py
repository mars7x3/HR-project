import requests

from myadmin.models import EntityAllHistory
from myadmin.utils import pay_history, plan_done
from test_wallet.models import Wallet, WalletHistory

def elsom_payment_create(receipt):
    payload = {
        "CultureInfo": "ru-RU",
        "MSISDN": receipt.user_phone,
        "PmSISDN": "0888555554",
        "PartnerCode": "89376",
        "Password": "Password1+",
        "ChequeNo": receipt.id,
        "PartnerTrnID": receipt.id,
        "Amount": receipt.amount,

    }
    url = 'https://93.170.8.101:8003/service/v1/merchant/generateToken'
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload, timeout=10, verify=False)
    return response.json()


def elsom_transaction_plus(receipt):
    payment = 'ElSom'
    amount = receipt.pg_amount
    wallet_id = receipt.wallet
    if amount and wallet_id:
        wallet = Wallet.objects.get(user__username=wallet_id)
        wallet.amount += int(amount)
        WalletHistory.objects.create(wallet=wallet, status='+', amount=amount, comment=payment,
                                     client=wallet.user.entity_profile.company)
        EntityAllHistory.objects.create(user=wallet.user, amount=amount, comment=payment, balance=wallet.amount)
        wallet.save()
        pay_history(wallet, amount, payment)
        if wallet.user.entity_profile.manager.exists():
            plan_done(wallet.user.entity_profile.manager.first(), amount)


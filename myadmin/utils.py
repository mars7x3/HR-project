from myadmin.models import Plan, PayHistory, Debtors


def plan_done(manager, amount: int):
    plan = Plan.objects.filter(manager=manager)
    if plan:
        plan.first().done += int(amount)
        plan.first().save()


def plan_done_refund(manager, amount: int):
    plan = Plan.objects.filter(manager=manager)
    amount = amount
    if plan:
        plan.first().done -= int(amount)
        plan.first().save()


def pay_history(wallet, amount, payment, comment):
    company = wallet.user.entity_profile.company
    PayHistory.objects.create(company=company, amount=amount, payment=payment, wallet=wallet, comment=comment)


def pay_history_refund(wallet, amount, payment, comment):
    company = wallet.user.entity_profile.company
    amount = -int(amount)
    PayHistory.objects.create(company=company, amount=amount, payment=payment, wallet=wallet, comment=comment)


def delete_debtor(wallet, amount):
    debtor = Debtors.objects.filter(company=wallet.user).first()
    amount = int(amount)

    if debtor:
        if debtor.transaction_amount < amount:
            debtor.transaction_amount += amount
            debtor.save()
            if wallet.amount >= 0:
                debtor.delete()

        if debtor.transaction_amount >= amount:
            debtor.delete()


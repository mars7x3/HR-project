from myadmin.models import Plan, PayHistory


def plan_done(manager, amount: int):
    plan = Plan.objects.filter(manager=manager)
    if plan:
        plan.first().done += int(amount)
        plan.first().save()


def pay_history(wallet, amount, payment, comment):
    company = wallet.user.entity_profile.company
    PayHistory.objects.create(company=company, amount=amount, payment=payment, wallet=wallet, comment=comment)

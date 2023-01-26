from accounts.models import MyUser


def get_user_mail():
    users = MyUser.objects.filter(user_status='applicant')
    result = []
    for u in users:
        if not u.resume.exists():
            result.append(u)
    print(len(result))


get_user_mail()

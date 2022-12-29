from django.utils.crypto import get_random_string

from accounts.gmail import SendMail


def generate_pwd() -> str:
    password = get_random_string(length=8,
                                 allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    return password


def generate_username(uid) -> str:
    uid = str(uid)
    number = '0' * (6 - len(uid))
    username = 'h' + number + uid
    return username


def send_pwd_and_username(username, password, email):
    text = f'Ваш логин: {username}\n Ваш пароль: {password}'
    SendMail(from_e='hr@hrgroup.kg', to_es=email, text=text).send()


def generate_activation_code():
    return get_random_string(length=4, allowed_chars='0123456789')


def send_activation_code(email, code):
    text = f'Ваш код активации: {code}'
    SendMail(from_e='hr@hrgroup.kg', to_es=email, text=text).send()


def send_new_pwd(password, email):
    text = f'Ваш новый пароль: {password}'
    SendMail(from_e='hr@hrgroup.kg', to_es=email, text=text).send()


def send_postings(posting):
    email = posting.vacancy.personal.email
    text = f'Соискатель {posting.resume.last_name} {posting.resume.name} откликнулся на вакансию '\
           f'http://hrgroup.kg/vacancies/{posting.vacancy.id}/\n'\
           f'Резюме соискателя http://hrgroup.kg/resumes/{posting.resume.id}/ .'
    SendMail(from_e='hr@hrgroup.kg', to_es=email, text=text).send()


# def send_moderation_response(password, email):
#     text = f'Ваш новый пароль: {password}'
#     SendMail(from_e='hr@hrgroup.kg', to_es=email, text=text).send()
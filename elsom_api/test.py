
import requests
import hashlib

# url = "test"


url = "https://api.freedompay.money/init_payment.php"

pg_merchant_id = '546026'
secret_key = '2SzFDcorJoJY2x38'


payload = {
    'pg_order_id': '29',
    'pg_merchant_id': pg_merchant_id,
    'pg_amount': '25',
    'pg_description': 'test',
    'pg_salt': 'molbulak',
    'pg_currency': 'KGS',
        # 'pg_check_url': 'http://hrgroup.kg/check',
    # 'pg_result_url': 'https://hrgroup.kg/result-transaction',
    # 'pg_request_method': 'POST',
    'pg_success_url': 'https://hrgroup.kg',
    'pg_failure_url': 'https://hrgroup.kg',
    'pg_success_url_method': 'GET',
    'pg_failure_url_method': 'GET',
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

}

def make_flat_params_array(data):
        flat_list = []
        for k, v in sorted(data.items()):
            flat_list.append(v)
        flat_list.insert(0, 'init_payment.php')
        flat_list.append(secret_key)
        return flat_list


def hash_for(data):
    data = data.encode()
    md5 = hashlib.md5(data).hexdigest()
    return md5


print(';'.join(make_flat_params_array(payload)))

payload['pg_sig'] = hash_for(';'.join(make_flat_params_array(payload)))
print(payload)
headers = {}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)



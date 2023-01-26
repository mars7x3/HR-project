import time
import requests

from main.celery import app
from .models import TransactionReceipt


@app.task()
def start_monitoring_cars(receipt_id):
    print('Start monitoring...')
    receipt = TransactionReceipt.objects.get(id=receipt_id)
    payload = {
        "CultureInfo": "ru-RU",
        "MSISDN": receipt.user_phone,
        "Password": "Password1+",
        "PartnerTrnID": receipt.id,
    }
    url = 'https://93.170.8.101:8003/service/v1/merchant/otp/1319'
    while True:
        response = requests.request("POST", url, data=payload)
        try:
            response = response.json()
            result = response.get('Response').get('Result')
            if result:
                receipt.status, receipt.message = result.get('PaymentStatus'), result.get('Message')
                receipt.save()
                print("Проверил")
        except Exception as e:
            print(e, end='\n\n')
            print(response.status_code, end='\n\n')
            print(response.text, end='\n\n___________________________________________')
            break

        if receipt.status != '1':
            break

        time.sleep(15)


# start_monitoring_cars.apply_async(eta=timezone.now() + datetime.timedelta(seconds=30))


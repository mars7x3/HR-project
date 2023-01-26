import requests
import json

url = "https://93.170.8.101:8003/service/v1/merchant/generateToken"

payload = json.dumps({
  "CultureInfo": "ru-RU",
  "MSISDN": "0313222222",
  "PmSISDN": "0888555554",
  "PartnerCode": "89376",
  "Password": "Password1+",
  "ChequeNo": "3",
  "PartnerTrnID": "3",
  "Amount": "33",
  "UDF": None,
  "CashierNo": None,
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False, timeout=10)

print(response.text)

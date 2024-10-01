import requests
from django.conf import settings
import json
import hashlib
import hmac

if settings.DEBUG:
    preferred_bank = "test-bank"
else:
    preferred_bank = "wema-bank"
class Paystack():
    def __init__(self, sk):
        self.paystack_sk = sk
        self.base_url = "https://api.paystack.co/"
    
    #============= Reserved Accounts ======================
    def createCustomer(self, **kwargs):
        path = f'customer'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        url = self.base_url + path

        data = {
            "email": kwargs['email'],
            "first_name": kwargs['firstName'],
            "last_name": kwargs["lastName"],
            "phone": kwargs['phoneNumber']
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return response_data['status'], response_data['data']
            response_data = response.json()
            return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    def validateBankAccount(self, **kwargs):
        path = f'customer/{kwargs["customer_code"]}/identification'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        url = self.base_url + path

        data = {
            "country": "NG",
            "type": "bank_account",
            "account_number": kwargs["account_number"],
            "bvn": kwargs['bvn'],
            "bank_code": kwargs["bank_code"],
            "first_name": kwargs['first_name'],
            "last_name": kwargs["last_name"]
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response_data = response.json()
            return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    def assignDedicatedAccount(self, **kwargs):
        path = f'dedicated_account'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        url = self.base_url + path

        data = {
            "customer": kwargs['customerId'],
            "phone": kwargs['phoneNumber'],
            "preferred_bank": preferred_bank
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return response_data['status'], response_data['data']
            response_data = response.json()
            return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    def createDedicatedAccount(self, **kwargs):
        path = f'dedicated_account/assign'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        url = self.base_url + path

        data = {
            "accountReference": kwargs['accountReference'],
            "accountName": kwargs['accountName'],
            "currencyCode": "NGN",
            "contractCode": self.contract_code,
            "customerEmail": kwargs['customerEmail'],
            "customerName": kwargs['customerName'],
            "bvn": kwargs['bvn'],
            "nin": kwargs['nin'],
            "getAllAvailableBanks": True,
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return response_data['status'], response_data['data']
            response_data = response.json()
            return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    #============ Transactions =========================
    def initializeTransaction(self, *args, **kwargs):
        path = f'transaction/initialize'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        data = {
            "email": kwargs["email"],
            "amount": kwargs["amount"],
            "channels": ["card"]
        }
        url = self.base_url + path
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            print(response.json())
            if response.status_code == 200:
                response_data = response.json()
                return response_data['status'], response_data['data']
            response_data = response.json()
            return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    def verifyTransaction(self, ref):
        path = f'transaction/verify/{ref}'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        url = self.base_url + path
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'], response_data['data']
        
        response_data = response.json()
        return response_data['status'], response_data['message']
    
    #============ Transfers =========================
    def initiateTransfer(self, *args, **kwargs):
        path = f'transfer'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        data = {
            "source": "balance",
            "amount": kwargs["amount"],
            "reason": kwargs["description"],
            "reference": kwargs["reference"],
            "recipient": kwargs["recipient_code"]
        }
        url = self.base_url + path
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response_data = response.json()
            #print(response_data)
            if response_data["status"]:
                return response_data['status'], response_data['data']
            else:
                return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    #============ Recipients =========================
    def createTransferRecipient(self, *args, **kwargs):
        path = f'transferrecipient'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        data = {
            "type": "nuban",
            "currency": "NGN",
            "name": kwargs["account_name"],
            "account_number": kwargs["account_number"],
            "bank_code": kwargs["bank_code"],
            
        }
        url = self.base_url + path
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response_data = response.json()
            if response_data["status"]:
                return response_data['status'], response_data['data']
            else:
                return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    #========= Accounts ==========================
    def getAccountBalance(self, *args, **kwargs):
        path = f'balance'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        url = self.base_url + path
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return response_data['status'], response_data['data']
            response_data = response.json()
            return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    #========= Verification ==========================
    def resolveAccountNumber(self, accountNumber, bankCode):
        path = f'bank/resolve?account_number={accountNumber}&bank_code={bankCode}'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        url = self.base_url + path
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return response_data['status'], response_data['data']
            response_data = response.json()
            return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    def resolveCardBin(self, cardBin):
        path = f'decision/bin/{cardBin}'
        headers = {
			"Authorization": f"Bearer {self.paystack_sk}",
			"Content-Type": "application/json",
		}
        url = self.base_url + path
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return response_data['status'], response_data['data']
            response_data = response.json()
            return response_data['status'], response_data['message']
        except Exception as e:
            return False, str(e)
    
    #=========== Webhooks ==============================
    def createHashFromWebhook(self, data):
        hash_object = hmac.new(self.paystack_sk.encode('utf-8'), json.dumps(data).encode('utf-8'), hashlib.sha512)
        hash_value = hash_object.hexdigest()
        return hash_value



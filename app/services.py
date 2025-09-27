import os
import requests
import json
from urllib.parse import urlencode

class SMSService:
    def __init__(self):
        self.username = os.getenv('AFRICASTALKING_USERNAME')
        self.api_key = os.getenv('AFRICASTALKING_API_KEY')
        self.api_url = "https://api.africastalking.com/version1/messaging"
        
        self.valid_credentials = (
            self.username and 
            self.api_key and 
            not any(x in self.username.lower() for x in ['your_', 'demo']) and
            not any(x in self.api_key.lower() for x in ['your_', 'demo'])
        )
    
    def send_order_confirmation(self, phone_number, order_name, price):
        if not self.valid_credentials:
            return self.demo_send(phone_number, order_name, price)
        
        return self.live_send(phone_number, order_name, price)
    
    def live_send(self, phone_number, order_name, price):
        # Send SMS using AT API
        try:
            formatted_phone = self.format_phone_number(phone_number)
            message = f"ORDER CONFIRMATION: {order_name} - ${price:.2f}. Thank you for your order!"
            
            # Prepare data for Africa's Talking 
            data = {
                'username': self.username,
                'to': formatted_phone,
                'message': message,
                'from': ''
            }
            
            headers = {
                'apiKey': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            # Send request
            response = requests.post(
                f"{self.api_url}/bulk",
                data=urlencode(data),
                headers=headers,
                timeout=30
            )
            
            print(f"Africa's Talking Response: {response.status_code} - {response.text}")
            
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"SMS sending error: {e}")
            return False
    
    def demo_send(self, phone_number, order_name, price):
        formatted_phone = self.format_phone_number(phone_number)
        print(f"DEMO: SMS to {formatted_phone}: {order_name} - ${price:.2f}")
        return True
    
    def format_phone_number(self, phone_number):
        if not phone_number.startswith('+'):
            if phone_number.startswith('0'):
                return '+254' + phone_number[1:]
            else:
                return '+' + phone_number
        return phone_number

sms_service = SMSService()
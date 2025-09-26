import pytest
import os
from unittest.mock import patch, MagicMock
import requests

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import SMSService

class TestSMSService:

    def setup_method(self):
        for key in ['AFRICASTALKING_USERNAME', 'AFRICASTALKING_API_KEY']:
            if key in os.environ:
                del os.environ[key]

    def test_demo_mode_works(self):
        service = SMSService()
        assert service.send_order_confirmation('+254712345678', 'Test', 99.99) is True

    @patch.dict(os.environ, {'AFRICASTALKING_USERNAME': 'user', 'AFRICASTALKING_API_KEY': 'key'})
    @patch('app.services.requests.post')
    def test_live_mode_works(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        service = SMSService()
        result = service.send_order_confirmation('0712345678', 'Test', 99.99)
        
        assert result is True
        mock_post.assert_called_once()

    def test_phone_formatting(self):
        service = SMSService()
        assert service.format_phone_number('0712345678') == '+254712345678'
        assert service.format_phone_number('+254712345678') == '+254712345678'
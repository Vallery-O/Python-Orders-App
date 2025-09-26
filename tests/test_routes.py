import pytest
from unittest.mock import patch, MagicMock
import os

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Customer, Order

class TestRoutes:

    @pytest.fixture
    def app(self):
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def init_db(self, app):
        with app.app_context():
            db.create_all()
            yield
            db.drop_all()

    @pytest.fixture
    def test_user(self, app, init_db):
        with app.app_context():
            user = User(google_id='test123', email='test@test.com', name='Test User')
            db.session.add(user)
            db.session.commit()
            return user

    @pytest.fixture
    def auth_client(self, client, test_user):
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
        return client

    def test_home_page(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Customer Order System' in response.data

    def test_dashboard_requires_auth(self, client):
        response = client.get('/dashboard')
        assert response.status_code in [302, 401]  # Redirect or unauthorized

    def test_dashboard_with_auth(self, auth_client, app, test_user):
        with app.app_context():
            customer = Customer(name='Test Customer', phone='+254712345678', created_by=test_user.id)
            db.session.add(customer)
            db.session.commit()

        response = auth_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Test Customer' in response.data

    @patch('app.routes.sms_service.send_order_confirmation')
    def test_create_order(self, mock_sms, auth_client, app, test_user):
        with app.app_context():
            customer = Customer(name='Test Customer', phone='+254712345678', created_by=test_user.id)
            db.session.add(customer)
            db.session.commit()

        mock_sms.return_value = True
        
        data = {
            'customer_id': customer.id,
            'order_name': 'New Order',
            'price': '99.99'
        }
        
        response = auth_client.post('/order', data=data)
        assert response.status_code == 200

    def test_api_health(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        assert b'healthy' in response.data

    def test_api_customers_with_auth(self, auth_client, app, test_user):
        with app.app_context():
            customer = Customer(name='API Customer', phone='+254712345678', created_by=test_user.id)
            db.session.add(customer)
            db.session.commit()

        response = auth_client.get('/api/customers')
        assert response.status_code == 200
        assert b'API Customer' in response.data
import pytest
from datetime import datetime
import os

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Customer, Order

class TestModels:

    @pytest.fixture
    def app(self):
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        return app

    @pytest.fixture
    def init_db(self, app):
        with app.app_context():
            db.create_all()
            yield
            db.drop_all()

    def test_user_creation(self, app, init_db):
        with app.app_context():
            user = User(google_id='test123', email='test@test.com', name='Test User')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.email == 'test@test.com'

    def test_customer_creation(self, app, init_db):
        with app.app_context():
            user = User(google_id='user123', email='user@test.com', name='User')
            customer = Customer(name='Test Customer', phone='+254712345678', created_by=user.id)
            
            db.session.add_all([user, customer])
            db.session.commit()
            
            assert customer.id is not None
            assert customer.user == user

    def test_order_creation(self, app, init_db):
        with app.app_context():
            user = User(google_id='user123', email='user@test.com', name='User')
            customer = Customer(name='Customer', phone='+254712345678', created_by=user.id)
            order = Order(order_name='Test Order', price=99.99, customer_id=customer.id, created_by=user.id)
            
            db.session.add_all([user, customer, order])
            db.session.commit()
            
            assert order.id is not None
            assert order.customer == customer
            assert order.user == user

    def test_order_to_dict(self, app, init_db):
        with app.app_context():
            user = User(google_id='user123', email='user@test.com', name='User')
            customer = Customer(name='Customer', phone='+254712345678', created_by=user.id)
            order = Order(order_name='Test Order', price=99.99, customer_id=customer.id, created_by=user.id)
            
            db.session.add_all([user, customer, order])
            db.session.commit()
            
            order_dict = order.to_dict()
            assert order_dict['order_name'] == 'Test Order'
            assert order_dict['price'] == 99.99
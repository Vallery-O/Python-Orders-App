import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import db
from app.models import User, Customer, Order

@pytest.mark.usefixtures("app")  # uses the fixture from tests/conftest.py
class TestModels:

    def test_user_creation(self, app):
        """Can create a User and persist it."""
        with app.app_context():
            u = User(
                google_id="google-123",
                email="test@example.com",
                name="Test User"
            )
            db.session.add(u)
            db.session.commit()

            fetched = User.query.first()
            assert fetched is not None
            assert fetched.google_id == "google-123"
            assert fetched.email == "test@example.com"
            assert fetched.name == "Test User"

    def test_customer_creation(self, app):
        """Can create a Customer linked to a User."""
        with app.app_context():
            u = User(google_id="g-222", email="c@example.com", name="Customer Owner")
            db.session.add(u)
            db.session.commit()

            c = Customer(
                name="ACME Corp",
                phone="+254700000000",
                created_by=u.id
            )
            db.session.add(c)
            db.session.commit()

            fetched = Customer.query.first()
            assert fetched is not None
            assert fetched.name == "ACME Corp"
            assert fetched.phone == "+254700000000"
            assert fetched.user == u  # backref works
            assert fetched.created_by == u.id

    def test_order_creation_and_to_dict(self, app):
        """Can create an Order linked to Customer and User and convert to dict."""
        with app.app_context():
            # Create user and customer first
            u = User(google_id="g-333", email="o@example.com", name="Order Owner")
            db.session.add(u)
            db.session.commit()

            c = Customer(
                name="Beta Ltd",
                phone="+254700000111",
                created_by=u.id
            )
            db.session.add(c)
            db.session.commit()

            o = Order(
                order_name="Widget",
                price=9.99,
                customer_id=c.id,
                created_by=u.id
            )
            db.session.add(o)
            db.session.commit()

            fetched = Order.query.first()
            assert fetched is not None
            assert fetched.order_name == "Widget"
            assert fetched.price == 9.99
            assert fetched.customer == c
            assert fetched.user == u

            # test to_dict
            d = fetched.to_dict()
            assert d["order_name"] == "Widget"
            assert d["price"] == 9.99
            assert d["customer_id"] == c.id
            assert d["customer_name"] == c.name
            assert "created_at" in d

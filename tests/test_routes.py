import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import db
from app.models import User, Customer, Order

@pytest.mark.usefixtures("app")
class TestRoutes:

    def test_health_endpoint(self, client):
        """Public health endpoint returns OK JSON."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "healthy"

    def _login_user(self, app, client):
        from app.models import User, db
        with app.app_context():
            u = User(google_id="123", email="test@example.com", name="Test")
            db.session.add(u)
            db.session.commit()
            user_id = u.id

            
            with client.session_transaction() as sess:
                sess["_user_id"] = str(user_id)  
                sess["_fresh"] = True
                
                return u


    def test_dashboard_route(client, app):
        with app.app_context():
            user = User(google_id="g123", email="test@example.com", name="Tester")
            db.session.add(user)
            db.session.commit()

        # Use the test client’s session_transaction to log the user in
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)  # Flask-Login stores user_id as string
            sess['_fresh'] = True            # mark session as fresh login

        # Now request the dashboard
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"Dashboard" in response.data
    

    def test_api_get_customers_and_orders(self, app, client):
        """Create a customer + order and check API endpoints."""
        u = self._login_user(app, client)

        # Create a customer directly in DB
        with app.app_context():
            c = Customer(name="Acme Ltd", phone="+254700000000", created_by=u.id)
            db.session.add(c)
            db.session.commit()

            o = Order(order_name="Widget", price=19.99, customer_id=c.id, created_by=u.id)
            db.session.add(o)
            db.session.commit()

        # call /api/customers
        resp = client.get("/api/customers")
        assert resp.status_code == 200
        customers_json = resp.get_json()
        assert len(customers_json) == 1
        assert customers_json[0]["name"] == "Acme Ltd"
        assert customers_json[0]["order_count"] == 1

        # call /api/orders
        resp2 = client.get("/api/orders")
        assert resp2.status_code == 200
        orders_json = resp2.get_json()
        assert len(orders_json) == 1
        assert orders_json[0]["order_name"] == "Widget"
        assert orders_json[0]["price"] == 19.99

    def test_create_customer_route(self, app, client):
        """POST /customer creates a customer and redirects."""
        u = self._login_user(app, client)

        resp = client.post(
            "/customer",
            data={"name": "Test Customer", "phone": "+254700000123"},
            follow_redirects=True,
        )
        assert resp.status_code == 200  # after redirect to dashboard

        with app.app_context():
            c = Customer.query.filter_by(name="Test Customer", created_by=u.id).first()
            assert c is not None
            assert c.phone == "+254700000123"

    def test_create_order_route(self, app, client, monkeypatch):
        u = self._login_user(app, client)
        with app.app_context():
            c = Customer(name="Order Customer", phone="+254700000321", created_by=u.id)
            db.session.add(c)
            db.session.commit()
            customer_id = c.id  # capture before leaving the context 
            
        from app import services
        monkeypatch.setattr(
            services.sms_service, "send_order_confirmation",
            lambda phone, name, price: True,
        )
        resp = client.post(
            "/order",
            data={"order_name": "Test Order", "price": "5.5", "customer_id": customer_id},
            follow_redirects=True,
            )
        assert resp.status_code == 200

        with app.app_context():
            o = Order.query.filter_by(order_name="Test Order", created_by=u.id).first()
            assert o is not None
            assert o.price == 5.5
            assert o.customer_id == c.id

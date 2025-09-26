import pytest
import os

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

class TestAppInit:

    def setup_method(self):
        # Clear relevant environment variables
        for key in ['SECRET_KEY', 'DATABASE_URL']:
            if key in os.environ:
                del os.environ[key]

    def test_app_creation(self):
        app = create_app()
        assert app is not None
        assert 'SECRET_KEY' in app.config

    def test_database_initialization(self):
        app = create_app()
        with app.app_context():
            # Should be able to create and drop tables
            db.create_all()
            db.drop_all()

    def test_blueprints_registered(self):
        app = create_app()
        assert 'main' in app.blueprints

    def test_error_handlers(self):
        app = create_app()
        client = app.test_client()
        
        response = client.get('/nonexistent-route')
        assert response.status_code == 404

    def test_user_loader(self, app):
        with app.app_context():
            from app.models import User
            user = User(google_id='loader123', email='loader@test.com', name='Loader')
            db.session.add(user)
            db.session.commit()
            
            from app import login_manager
            loaded_user = login_manager._user_callback(user.id)
            assert loaded_user.id == user.id
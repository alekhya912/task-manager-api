import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from app import app
from extensions import db


@pytest.fixture
def client():
    app.config["TESTING"] = True

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql+psycopg://postgres:Alekhya@localhost:5432/task_manager_test_db"
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()

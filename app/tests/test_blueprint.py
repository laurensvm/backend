import os
import unittest
import json

from backend.app import create_app, db
from backend.app.models import User

from base64 import b64encode

class TestBase(unittest.TestCase):
    def setUp(self):
        app = create_app()

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.config["BASEDIR"], 'test.db')

        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

        db.create_all()

        self.create_user()

    def tearDown(self):
        with self.ctx:
            db.session.remove()
            db.drop_all()

    def create_user(self):
        # Create client side copy of credentials
        self.user_dict = dict(email="test@test.com", username="test", password="test")

        self.user = User(
            email=self.user_dict["email"],
            username=self.user_dict["username"],
            password=self.user_dict["password"],
            admin=True
        )

        db.session.add(self.user)
        db.session.commit()

        self.user_dict["id"] = User.query.filter_by(username=self.user_dict["username"]).first().id

    def get_header(self):
        string = "{0}:{1}".format(self.user_dict["email"], self.user_dict["password"])
        header = dict(Authorization="Basic {user}".format(user=b64encode(string.encode()).decode("ascii")))
        header["Content-Type"] = "application/json"
        return header

    def parse_json(self, data):
        return json.loads(data.decode("utf-8"))

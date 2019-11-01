import unittest
import json

from .test_blueprint import TestBase

class TestAuthentication(TestBase):

    def setUp(self):
        super(TestAuthentication, self).setUp()
        self.test_user = dict(username="test1", email="test1@test.com", password="test1")

    def test_token(self):
        response = self.app.get("/auth/token/", headers=self.get_header())
        data = self.parse_json(response.data)
        assert data.get("expiration") == 3600

    def test_get_users(self):
        response = self.app.get("/auth/users/", headers=self.get_header())
        data = self.parse_json(response.data)
        assert data.get("users") is not None

    def test_get_user_by_username(self):
        response = self.app.get("/auth/users/{0}/".format(self.user_dict["username"]), headers=self.get_header())
        data = self.parse_json(response.data)
        assert self.user_dict["email"] == data.get("email")

    def test_get_user_by_id(self):
        response = self.app.get("/auth/users/{0}/".format(self.user_dict["id"]), headers=self.get_header())
        data = self.parse_json(response.data)
        assert self.user_dict["email"] == data.get("email")

    def test_create_user(self):

        self.app.post("/auth/users/create/",
            headers=self.get_header(),
            content_type="application/json",
            data=json.dumps(self.test_user)
        )

        response = self.app.get("/auth/users/{0}/".format(self.test_user["username"]), headers=self.get_header())
        data = self.parse_json(response.data)
        assert self.test_user["email"] == data.get("email")

    def test_delete_user(self):
        self.app.post("/auth/users/create/",
            headers=self.get_header(),
            content_type="application/json",
            data=json.dumps(self.test_user)
        )

        response = self.app.get("/auth/users/delete/{0}/".format(self.test_user["username"]), headers=self.get_header())
        data = self.parse_json(response.data)
        assert data.get("success") == "OK"

    def test_update_user(self):
        pass

    # Implement testing methods for negative use cases/alternative routes

if __name__ == '__main__':
    unittest.main()
import unittest

from .test_blueprint import TestBase

class TestAuthentication(TestBase):

    def test_token(self):
        response = self.app.get("/auth/token/", headers=self.get_header())
        data = self.parse_json(response.data)
        assert data.get("expiration") == 3600

    def test_get_users(self):
        response = self.app.get("/auth/users/", headers=self.get_header())
        data = self.parse_json(response.data)
        assert data.get("users") is not None

    def test_get_user(self):
        pass

    def test_create_user(self):
        pass

    def test_delete_user(self):
        pass


if __name__ == '__main__':
    unittest.main()
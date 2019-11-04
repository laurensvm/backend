import unittest
import json

from .test_blueprint import TestBase

class TestDirectories(TestBase):

    def test_get_latest_directory(self):
        response = self.app.get("/directories/", headers=self.get_header())
        data = self.parse_json(response.data)
        assert data["directories"][0].get("id") == 1

    def test_root_directory(self):
        response = self.app.get("/directories/root/", headers=self.get_header())
        data = self.parse_json(response.data)
        assert data.get("name") == self.app.application.config["ROOT_FOLDER"]

    def test_get_directory_by_id(self):
        id = 1
        response = self.app.get("/directories/{0}/".format(id), headers=self.get_header())
        data = self.parse_json(response.data)
        assert data.get("id") == id

    def test_get_directory_children_by_id(self):
        id = 1
        response = self.app.get("/directories/{0}/files/".format(id), headers=self.get_header())
        data = self.parse_json(response.data)
        # Might have to add a file and retrieve it again
        assert data.get("files") == []

    def test_rename_directory(self):
        id = 1
        dirname = "test_directory"

        # Create a new directory
        self.app.post("/directories/create/",
                      headers=self.get_header(),
                      content_type="application/json",
                      data=json.dumps(dict(parent_id=id, name=dirname))
                      )

        path = "{0}/{1}".format(self.app.application.config["ROOT_FOLDER"], dirname)

        # Get the new directories id
        response = self.app.post("/directories/id/",
                                 headers=self.get_header(),
                                 content_type="application/json",
                                 data=json.dumps(dict(path=path))
                                )

        id = self.parse_json(response.data).get("id")

        name = "new_test_root"
        self.app.post("/directories/{0}/rename/".format(id),
                      headers=self.get_header(),
                      content_type="application/json",
                      data=json.dumps(dict(name=name))
                      )

        response = self.app.get("/directories/{0}/".format(id), headers=self.get_header())
        data = self.parse_json(response.data)
        assert data.get("name") == name

    def test_get_directory_rights(self):
        pass

    def test_delete_directory(self):
        pass


if __name__ == '__main__':
    unittest.main()
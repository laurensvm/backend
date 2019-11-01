import enum

class ValidationError(ValueError):
    pass


class IOException(IOError):

    def __init__(self, type, message=None):
        if message:
            super(IOException, self).__init__(message)
        else:
            super(IOException, self).__init__(type.value)

    def json(self):
        return dict(message=self.message)

    class Type(enum.Enum):
        path_does_not_exist = "Path does not exist"
        path_already_exists = "Cannot save file. The file path already exists"
        insufficient_rights = "User has insufficient rights to perform IO operations in this directory"

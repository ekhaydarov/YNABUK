from enum import Enum


class BaseEnum(Enum):

    def __str__(self):
        return str(self.value)


class TimeFormats(BaseEnum):
    DATE = '%Y-%m-%d'
    TRUELAYER_DATETIME = '%Y-%m-%dT%H:%M:%S%z'


class APIMethods(BaseEnum):
    GET = 'get'
    POST = 'post'
    DELETE = 'delete'
    UPDATE = 'update'
    PATCH = 'patch'

from exceptions import Exception


class InconsistencyException(Exception):
    pass


class InvalidId(Exception):
    pass


class DuplicateEntry(Exception):
    pass


class NotFound(Exception):
    pass


class NotAllowed(Exception):
    pass


class InvalidZone(Exception):
    pass

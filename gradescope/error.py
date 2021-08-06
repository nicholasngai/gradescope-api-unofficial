class GSInvalidRequestException(Exception):
    pass

class GSNotAuthorizedException(GSInvalidRequestException):
    pass

class GSInternalException(Exception):
    pass

class StatusPinExceptions(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self, message)


class ErrorProcessReturnSMSMarket(StatusPinExceptions):
    def __init__(self, message='An error has occurred to process return from SMS Market'):
        self.message = message
        self.code = 500
        super(ErrorProcessReturnSMSMarket, self).__init__(self.message, self.code)


class AuthenticationErrorOnSMSMarket(StatusPinExceptions):
    def __init__(self, message='An error has occurred with authentication on SMS Market, user or password incorrect'):
        self.message = message
        self.code = 401
        super(AuthenticationErrorOnSMSMarket, self).__init__(self.message, self.code)

class MsisdnNotMatchFormat(StatusPinExceptions):
    def __init__(self, message='Msisdn format not match, try using DDI+DDD+Mobile_Number (5511912345678)'):
        self.message = message
        self.code = 400
        super(MsisdnNotMatchFormat, self).__init__(self.message, self.code)
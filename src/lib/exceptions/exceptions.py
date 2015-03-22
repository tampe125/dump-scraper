__author__ = 'Davide Tampellini'
__copyright__ = '2015 Davide Tampellini - FabbricaBinaria'
__license__ = 'GNU GPL version 3 or later'


class InvalidSettings(Exception):
    def __init__(self, message):
        super(InvalidSettings, self).__init__(message)

    def __str__(self):
        return self.message


class RunningError(Exception):
    def __init__(self, message):
        super(RunningError, self).__init__(message)

    def __str__(self):
        return self.message
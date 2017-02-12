# -*- coding: utf-8 -*-


class IsExistException(BaseException):
    pass


class IsNotExistException(BaseException):
    pass


class IsLockedException(BaseException):
    pass


class IsUnlockedException(BaseException):
    pass

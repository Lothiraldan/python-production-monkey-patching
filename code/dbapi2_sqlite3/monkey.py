import sys
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader


def patcher(function):
    def wrapper(*args, **kwargs):
        print("Patcher called with", args, kwargs)
        return function(*args, **kwargs)
    return wrapper


class CursorProxy(object):
    def __init__(self, cursor):
        self.cursor = cursor

        self.execute = patcher(self.cursor.execute)

    def __getattr__(self, key):
        return getattr(self.cursor, key)


class ConnectionProxy(object):
    def __init__(self, connection):
        self.connection = connection

    def cursor(self, *args, **kwargs):
        real_cursor = self.connection.cursor(*args, **kwargs)
        return CursorProxy(real_cursor)

    def __getattr__(self, key):
        return getattr(self.cursor, key)


def patch_connect(real_connect):
    def connect(*args, **kwargs):
        real_connection = real_connect(*args, **kwargs)
        return ConnectionProxy(real_connection)
    return connect


class CustomLoader(SourceFileLoader):

    def exec_module(self, module):
        super().exec_module(module)
        module.connect = patch_connect(module.connect)
        return module


class Finder(PathFinder):

    def __init__(self, module_name):
        self.module_name = module_name

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super().find_spec(fullname, path, target)
            return ModuleSpec(fullname,
                              CustomLoader(fullname, spec.origin))


def patch():
    sys.meta_path.insert(0, Finder('sqlite3.dbapi2'))

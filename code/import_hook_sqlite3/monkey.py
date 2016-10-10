import sys
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader


def patcher(function):
    def wrapper(*args, **kwargs):
        print("Patcher called with", args, kwargs)
        return function(*args, **kwargs)
    return wrapper


class CustomLoader(SourceFileLoader):

    def exec_module(self, module):
        super().exec_module(module)
        module.Cursor.execute = patcher(module.Cursor.execute)
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

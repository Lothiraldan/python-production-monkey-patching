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
        module.function = patcher(module.function)
        return module


class Finder(PathFinder):

    def __init__(self, module_name):
        self.module_name = module_name

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super().find_spec(fullname, path, target)
            loader = CustomLoader(fullname, spec.origin)
            return ModuleSpec(fullname, loader)


def patch():
    sys.meta_path.insert(0, Finder('module'))

def patcher(function):
    def wrapper(*args, **kwargs):
        print("Patcher called with", args, kwargs)
        return function(*args, **kwargs)
    return wrapper


def patch():
    import module
    module.function = patcher(module.function)

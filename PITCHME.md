#HSLIDE

## Pycon-fr 2016

Python monkey-patching in production.

#VSLIDE

## About-me @lothiraldan

 * Python developer

<img src="images/me.png" width="400" height="400"/>

#VSLIDE

## Sqreen.io

I work at sqreen.io where we bring security to every developer.

<img src="images/sqreen.png" width="400" height="400"/>

#HSLIDE

## Need

We need to provide an easy way to protect against SQL injections.

```python
import sql_protection
sql_protection.start()
```

#HSLIDE

## My first reaction

<img src="images/fry.png">

#HSLIDE

## Monkey-patching in production 101

#HSLIDE

## This slidedeck is Python3 compatible!

#HSLIDE

## First try - setattr

File module.py:

```python
def function(*args, **kwargs):
    print("Function called with", args, kwargs)
```

#VSLIDE

## Monkey-patching

File monkey.py:

```python
def patcher(function):
    def wrapper(*args, **kwargs):
        print("Patcher called with", args, kwargs)
        return function(*args, **kwargs)
    return wrapper

def patch():
    import module
    module.function = patcher(module.function)
```

#VSLIDE

## Test

```python
>>> import monkey
>>> monkey.patch()
>>> import module
>>> module.function('a', 'b', c='d')
Patcher called with ('a', 'b') {'c': 'd'}
Function called with ('a', 'b') {'c': 'd'}
```

```python
>>> import module
>>> import monkey
>>> monkey.patch()
>>> module.function('a', 'b', c='d')
Patcher called with ('a', 'b') {'c': 'd'}
Function called with ('a', 'b') {'c': 'd'}
```

#VSLIDE

## Done, not so hard!

#VSLIDE

## Not so fast

```python
>>> from module import function
>>> import monkey
>>> monkey.patch()
>>> function('a', 'b', c='d')
Function called with ('a', 'b') {'c': 'd'}
```

#VSLIDE

## Why?

```python
>>> module = {'function': 'FUNCTION'}
>>> function = module['function']
>>> module['function'] = 'FUNCTION_WRAPPED'
>>> print(function)
FUNCTION
>>> print(module['function'])
FUNCTION_WRAPPED
```

#VSLIDE

## Explanation

setattr only replace the name of the function / method / class in the module. If someone get another reference (with `from module import function`), we will not replace it.

#VSLIDE

## Hacks

There are some hacks around altering ```__code__``` attributes and retrieving references with `gc.get_referrers` but they're hacks and CPython specifics.

#HSLIDE

## Import hooks

#VSLIDE

## PEP

The idea is to use a `hook` to execute code just before a module is imported.

https://www.python.org/dev/peps/pep-0302/

#VSLIDE

## Python 2

```python
import sys

class Finder(object):

    def __init__(self, module_name):
        self.module_name = module_name

    def find_module(self, fullname, path=None):
        if fullname == self.module_name: 
            return self
        return

    def load_module(self, fullname):
        module = __import__(fullname)
        return customize_module(module)

sys.meta_path.insert(0, Finder('module'))
```

#VSLIDE

## Python 3

```python
import sys
from importlib.machinery import PathFinder, ModuleSpec

class Finder(PathFinder):

    def __init__(self, module_name):
        self.module_name = module_name

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super().find_spec(fullname, path, target)
            return ModuleSpec(fullname,
                              CustomLoader(fullname, spec.origin))

sys.meta_path.insert(0, Finder('module'))
```

#VSLIDE

## Python 3 - II

```python
from importlib.machinery import SourceFileLoader

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
```

#VSLIDE

## Full code

```python
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
            return ModuleSpec(fullname,
                              CustomLoader(fullname, spec.origin))

def patch():
    sys.meta_path.insert(0, Finder('module'))
```

#VSLIDE

## New try

```python
>>> import monkey
>>> monkey.patch()
>>> from module import function
>>> function('a', 'b', c='d')
Patcher called with ('a', 'b') {'c': 'd'}
Function called with ('a', 'b') {'c': 'd'}
```

#VSLIDE

## We dit it!

Or do we?

#VSLIDE

## Real code

File module.py:

```python
import sqlite3

def query(query):
    connection = sqlite3.connect('db.sqlite')
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchone()
```

#VSLIDE

## What module should we hook?

```python
>>> import sqlite3
>>> connection = sqlite3.connect('db.sqlite')
>>> cursor = connection.cursor()
>>> type(cursor)
<class 'sqlite3.Cursor'>
```

#VSLIDE

## Great let's patch it!

```python
...

class CustomLoader(SourceFileLoader):

    def exec_module(self, module):
        super().exec_module(module)
        module.Cursor.execute = patcher(module.Cursor.execute)
        return module
...
def patch():
    sys.meta_path.insert(0, Finder('sqlite3'))
```

#VSLIDE

## Should works, right?

```python
>>> import monkey
>>> monkey.patch()
>>> import module
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File ".../code/import_hook_sqlite3/module.py", line 1, in <module>
    import sqlite3
  File ".../code/import_hook_sqlite3/monkey.py", line 15, in exec_module
    super().exec_module(module)
  File ".../sqlite3/__init__.py", line 23, in <module>
    from sqlite3.dbapi2 import *
ImportError: No module named 'sqlite3.dbapi2'; 'sqlite3' is not a package
```

#VSLIDE

## Should be sqlite3.dbapi2

```python
...
def patch():
    sys.meta_path.insert(0, Finder('sqlite3.dbapi2'))
```

#VSLIDE

## Another try

```python
>>> import monkey
>>> monkey.patch()
>>> import module
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File ".../code/import_hook_sqlite3/module.py", line 1, in <module>
    import sqlite3
  File ".../sqlite3/__init__.py", line 23, in <module>
    from sqlite3.dbapi2 import *
  File "<frozen importlib._bootstrap>", line 969, in _find_and_load
  File "<frozen importlib._bootstrap>", line 958, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 673, in _load_unlocked
  File ".../monkey.py", line 16, in exec_module
    module.Cursor.execute = patcher(module.Cursor.execute)
TypeError: can't set attributes of built-in/extension type 'sqlite3.Cursor'
```

#HSLIDE

## C-defined classes

Sometimes classes are defined in C, making ```setattr``` useless.

#HSLIDE

## CLI LAUNCHER

Sometimes, people prefer a CLI launcher instead of modifying their code.

```bash
sql-protect python myapp.py
```

#VSLIDE

## sitecustomize.py

#VSLIDE

## Import lock

#HSLIDE

## Deinstrumentation

#VSLIDE

## Extract the callbacks

#HSLIDE

## Bonus

The real code you can use is:

```python
import sqreen
sqreen.start()
```

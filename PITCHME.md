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

<img src="images/python3.png" height="400"/>

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

https://www.python.org/dev/peps/pep-0249/

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
            loader = CustomLoader(fullname, spec.origin)
            return ModuleSpec(fullname, loader)

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
            loader = CustomLoader(fullname, spec.origin)
            return ModuleSpec(fullname, loader)

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
  File ".../module.py", line 1, in <module>
    import sqlite3
  File ".../monkey.py", line 15, in exec_module
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
  File ".../module.py", line 1, in <module>
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

With user-defined class, we can override everything we wants, but with built-in or extension defined class, it's much more harder.

#VSLIDE

## Setattr useless

```python
>>> from sqlite3.dbapi2 import Cursor
>>> Cursor.execute = lambda *args, **kwargs: 42
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can't set attributes of built-in/extension type 'sqlite3.Cursor'
```

#VSLIDE

## Parent

We can bypass the problem by patching the method that returns a Cursor, it is the `Connection.cursor` method.

```python
>>> from sqlite3.dbapi2 import Cursor
>>> Connection.cursor = lambda *args, **kwargs: 42
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can't set attributes of built-in/extension type 'sqlite3.Connection'
```

#VSLIDE

## The grand-parent

As we can't override `Connection` methods either, we need to patch the function that returns a `Connection`, it is `connect`:

```python
>>> import sqlite3
>>> sqlite3.connect = lambda *args, **kwargs: 42
>>> sqlite3.connect('db.sqlite')
42
```

#VSLIDE

## DBApi2

Luckily for us, every SQL driver follow the DBApi2 defined in pep 249 https://www.python.org/dev/peps/pep-0302/.

The DBApi2 defines the current interface:

```python
from sql_driver import connect
connection = connect(...)
cursor = connection.cursor()
cursor.execute(sql_query)
row = cursor.fetchone()
```

#VSLIDE

## Work to do

So we need to patch `connect`, `Connection.cursor` and `Cursor.execute`.

#VSLIDE

## Cursor

```python
class CursorProxy(object):
    def __init__(self, cursor):
        self.cursor = cursor

        self.execute = patcher(self.cursor.execute)

    def __getattr__(self, key):
        return getattr(self.cursor, key)
```

#VSLIDE

## Connection

```python
class ConnectionProxy(object):
    def __init__(self, connection):
        self.connection = connection

    def cursor(self, *args, **kwargs):
        real_cursor = self.connection.cursor(*args, **kwargs)
        return CursorProxy(real_cursor)

    def __getattr__(self, key):
        return getattr(self.cursor, key)
```

#VSLIDE

## connect

```python
def patch_connect(real_connect):
    def connect(*args, **kwargs):
        real_connection = real_connect(*args, **kwargs)
        return ConnectionProxy(real_connection)
    return connect
```

#VSLIDE

## Test

```python
>>> import monkey
>>> monkey.patch()
>>> import module
>>> module.query("SELECT 1;")
Patcher called with ('SELECT 1;',) {}
(1,)
```

#VSLIDE

# HOURAY!

#HSLIDE

## CLI LAUNCHER

Sometimes, people prefer a CLI launcher instead of modifying their code.

```bash
sql-protect gunicorn myapp.py
```

#VSLIDE

## How to execute code before the main app?

#VSLIDE

## We can setup import hooks now but then we must launch gunicorn

#VSLIDE

## How to execute gunicorn after setting the import hooks?

#VSLIDE

## Quite easily

```python
import sys
import os
os.execvpe(sys.argv[1:])
```

#VSLIDE

## Let's try to setup import hooks then exec

#VSLIDE

## Long story short, it don't work.

`os.execvpe` replace the current process with a new one, all memory is destroyed.

#VSLIDE

## How to execute code in gunicorn

#VSLIDE

## There is one to execute code before anything in Python

```python
$> python -v
import _frozen_importlib # frozen
import _imp # builtin
import sys # builtin
...
import 'sitecustomize' # ... <-
import 'site' # ...
Python 3.5.2 (default, Sep 28 2016, 18:08:09)
[GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.38)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
```

#VSLIDE

## site and sitecustomize modules

`site` is automatically imported by Python at startup to setup some search paths. It's in the standard library.
After importing `site`, Python try to import the module `sitecustomize`, it's not present by default but could be created and would be imported automatically.

#VSLIDE

## Caveat

The `sitecustomize.py` must be present somewhere in the search paths of Python.

#VSLIDE

## Here is the trick

But we can customize these paths with the environment variable `PYTHONPATH`!

#VSLIDE

## Final cli helper

File `sql-protect`:

```python
#!/usr/bin/env python

import sys
import os
from os.path import curdir, realpath

environ = os.environ
environ['PYTHONPATH'] = realpath(curdir)
os.execvpe(sys.argv[1], sys.argv[1:], environ)
```

#VSLIDE

## Final sitecustomize.py

Same content as previously in monkey.py, but with a new line at the end:

```python
def patch():
    sys.meta_path.insert(0, Finder('sqlite3.dbapi2'))

patch()
```

#VSLIDE

## Test it

```python
$> ./sql-protect python
Python 3.5.1 (default, Jan 22 2016, 08:54:32)
[GCC 4.2.1 Compatible Apple LLVM 7.0.2 (clang-700.1.81)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import module
>>> module.query('SELECT 1;')
Patcher called with ('SELECT 1;',) {}
(1,)
```

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

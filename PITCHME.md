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

#VSLIDE

## Setattr

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

import module
module.function = patcher(module.function)
```

#VSLIDE

## Test

```python
>>> import monkey
>>> import module
>>> module.function('a', 'b', c='d')
Patcher called with ('a', 'b') {'c': 'd'}
Function called with ('a', 'b') {'c': 'd'}
```

## Test bis

```python
>>> import module
>>> import monkey
>>> module.function('a', 'b', c='d')
Function called with ('a', 'b') {'c': 'd'}
```

#VSLIDE

## Not so fast

```python
>>> from module import function
>>> import monkey
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

## C-defined classes

Sometimes classes are defined in C, making ```setattr``` useless.

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

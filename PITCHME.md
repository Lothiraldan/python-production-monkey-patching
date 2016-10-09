#HSLIDE

## Pycon-fr

Python hot monkey-patching.

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

## Test

```python
>>> import monkey
>>> import module
>>> monkey.function('a', 'b', c='d')
Patcher called with ('a', 'b') {'c': 'd'}
Function called with ('a', 'b') {'c': 'd'}
```

#HSLIDE

## Bonus

The real code you can use is:

```python
import sqreen
sqreen.start()
```

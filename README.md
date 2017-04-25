# Pire

Pire tries to decomplect error handling and logic. It provides decorators to modify callable objects by adding meta information to them as a special attribute.

When a decorated callable is called by itself it behaves as usual, but if it's called with the help of a special supervising function (or is additionally decorated) then `pire` does its thing.

This is a recreation of a Clojure library called [dire](https://github.com/MichaelDrogalis/dire).

## Installation
```
pip install pire
```

## Drop-in Usage

### Simple Example

```python
from pire import excepting, supervised

# 'e' is the exception object, 'args' are the original arguments to the task.
def zero_div_handler(e, *args):
    print('Cannot divide by 0.')

# Define a task to run. It's just a function.
# For a task, specify an exception that can be raised and a function to deal with it.
@supervised
@excepting(ZeroDivisionError, zero_div_handler)
def divider(a, b):
    return a / b

divider(10, 0) # => "Cannot divide by 0."
```

### Multiple Exception Classes

```python
from pire import excepting, supervised

def general_handler(e, *args):
    print('Cannot divide by 0 or operate on None values.')

@supervised
@excepting([ZeroDivisionError, TypeError], general_handler)
def divider(a, b):
    return a / b

divider(10, 0) # => "Cannot divide by 0 or operate on None values."
divider(10, None) # => "Cannot divide by 0 or operate on None values."
```

### Try/Catch/Finally Semantics

```python
from pire import excepting, finally_call, supervised

# 'e' is the exception object, 'args' are the original arguments to the task.
def zero_div_handler(e, *args):
    print('Cannot divide by 0.')

def finally_clause(e, *args):
    print('Executing a finally clause.')

# Define a task to run. It's just a function.
# For a task, specify an exception that can be raised and a function to deal with it.
@supervised
@excepting(ZeroDivisionError, zero_div_handler)
@finally_call(finally_clause)
def divider(a, b):
    return a / b

divider(10, 0) # => "Cannot divide by 0.\nExecuting a finally clause.\n"
```

### Skipping handlers

```python
from pire import excepting, skipping, supervised

broad_selector = (ZeroDivisionError, TypeError)

def general_handler(e, *args):
    print('Cannot divide by 0 or operate on None values.')

@supervised
@excepting(broad_selector, general_handler)
def divider(a, b):
    return a / b

@supervised
@excepting(broad_selector, general_handler)
@skipping(ZeroDivisionError)
def another_divider(a, b):
    return a / b

divider(10, None) # => "Cannot divide by 0 or operate on None values."
divider(10, 0) # => "Cannot divide by 0 or operate on None values."

another_divider(10, None) # => "Cannot divide by 0 or operate on None values."
another_divider(10, 0) # An exception is raised.
```

## Erlang Style Usage (with supervise)

### Simple Example

```python
from pire import excepting, supervise

# 'e' is the exception object, 'args' are the original arguments to the task.
def zero_div_handler(e, *args):
    print('Cannot divide by 0.')

# Define a task to run. It's just a function.
# For a task, specify an exception that can be raised and a function to deal with it.
@excepting(ZeroDivisionError, zero_div_handler)
def divider(a, b):
    return a / b

supervise(divider, 10, 0) # => "Cannot divide by 0."
```

# Pire

Decomplect error logic with Erlang-style supervisor error handling for Python. This is a clone of a Clojure library called [dire](https://github.com/MichaelDrogalis/dire).

Ships in two flavors:
* The drop-in style, using a decorator
* Erlang-style inspired by the work of Joe Armstrong using a supervisor

## Installation
```
pip install pire
```

## Usage: Drop-in Flavor

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
@excepting((ZeroDivisionError, TypeError), general_handler)
def divider(a, b):
    return a / b

divider(10, 0) # => "Cannot divide by 0 or operate on None values."
divider(10, None) # => "Cannot divide by 0 or operate on None values."
```

### Try/Catch/Finally Semantics

```python
from pire import excepting, with_finally, supervised

# 'e' is the exception object, 'args' are the original arguments to the task.
def zero_div_handler(e, *args):
    print('Cannot divide by 0.')

def finally_clause(e, *args):
    print('Executing a finally clause.')

# Define a task to run. It's just a function.
# For a task, specify an exception that can be raised and a function to deal with it.
@supervised
@excepting(ZeroDivisionError, zero_div_handler)
@with_finally(finally_clause)
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

## Usage: Erlang Style with supervise

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

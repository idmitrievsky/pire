# -*- coding: utf-8 -*-

from enum import Enum
from functools import wraps
from inspect import isclass
from collections import OrderedDict

_pire_attr = '_pire_meta'


def _get_pire_meta(obj):
    if not hasattr(obj, _pire_attr):
        setattr(obj, _pire_attr, {'error_handlers': OrderedDict(),
                                  'ignored_handlers': set()})

    return getattr(obj, _pire_attr)


def with_handler(exception_selector, handler_fn):
    def decorator(task):
        task_meta = _get_pire_meta(task)
        err_handlers = task_meta['error_handlers']
        err_handlers[exception_selector] = handler_fn
        return task

    return decorator


def ignore_handler(exception_selector):
    def decorator(task):
        task_meta = _get_pire_meta(task)
        task_meta['ignored_handlers'].add(exception_selector)
        return task

    return decorator


def with_finally(finally_handler):
    def decorator(task):
        task_meta = _get_pire_meta(task)
        task_meta['finally'] = finally_handler
        return task

    return decorator


def _remove_finally(task):
    task_meta = _get_pire_meta(task)
    task_meta.pop('finally')
    return task


class _SelectorType(Enum):
    exc_class = 1
    exc_classes = 2
    unknown = 3


def _selector_type(exception_selector):
    if isclass(exception_selector) and issubclass(exception_selector, Exception):
        return _SelectorType.exc_class
    elif isinstance(exception_selector, tuple) and all(
                    isclass(s) and issubclass(s, Exception) for s in exception_selector):
        return _SelectorType.exc_classes
    else:
        return _SelectorType.unknown


def _does_selector_match(exception_selector, thrown_obj):
    s_type = _selector_type(exception_selector)

    if s_type == _SelectorType.exc_class:
        return isinstance(thrown_obj, exception_selector)
    elif s_type == _SelectorType.exc_classes:
        return any(isinstance(thrown_obj, s) for s in exception_selector)
    elif s_type == _SelectorType.unknown:
        return False

    return False


def _matching_handler(err_handlers, thrown_obj):
    for selector, err_handler in err_handlers.items():
        if _does_selector_match(selector, thrown_obj):
            return err_handler


def _apply_handler(task_meta, thrown_obj, *args, **kwargs):
    err_handler = _matching_handler(task_meta['error_handlers'], thrown_obj)
    is_active = err_handler and not any(isinstance(thrown_obj, i) for i in task_meta['ignored_handlers'])
    if is_active:
        err_handler(thrown_obj, *args, **kwargs)
    return is_active


def _eval_finally(task_meta, *args, **kwargs):
    if 'finally' in task_meta:
        return task_meta.get('finally')(*args, **kwargs)


def supervise(task, *args, **kwargs):
    task_meta = _get_pire_meta(task)
    try:
        return task(*args, **kwargs)
    except Exception as thrown_obj:
        if not _apply_handler(task_meta, thrown_obj, *args, **kwargs):
            raise
    finally:
        return _eval_finally(task_meta, *args, **kwargs)


def supervised(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return supervise(fn, *args, **kwargs)

    # if not applied any modifiers
    if hasattr(wrapper, _pire_attr):
        delattr(wrapper, _pire_attr)

    return wrapper

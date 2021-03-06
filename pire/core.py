# -*- coding: utf-8 -*-
"""
Pire tries to decomplect error handling from logic. It provides
decorators to modify callable objects by adding meta informationrmation
to them as a special attribute.

When decorated callable is called by itself it behaves as usual,
but if it's called with the help of a special supervising function
(or is additionally decorated) then `pire` does its thing.
"""

from functools import wraps
"""
Pire stores its meta information as an object attribute.
"""
_pire_attr = '_pire_meta'


def _empty_pire_meta():
    """
    Meta information is not just a dict. Explicitly keeping
    classes that don't need to be handled allows to apply
    `excepting` and `skipping` decorators in any order.
    The order of `excepting` decorators does matter though.
    The highest handler registered for a selector takes precedence.
    """
    return {'handlers_by_selector': {}, 'raising_classes': set()}


def _pire_meta(obj):
    """
    Any of the decorators can be applied first, so meta
    information is initialized lazily.
    """
    if not hasattr(obj, _pire_attr):
        setattr(obj, _pire_attr, _empty_pire_meta())

    return getattr(obj, _pire_attr)


def _is_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False

    return True


def excepting(selector, handler_fn):
    """
    Selector is not necessarily just an `Exception` subclass.
    Potentially it can be an id for any purpose, not just exception handling.

    It also can be an iterable of these things to register general
    handlers.
    """

    def decorator(task):
        task_meta = _pire_meta(task)
        handlers_by_selector = task_meta['handlers_by_selector']
        if _is_iterable(selector):
            for s in selector:
                handlers_by_selector[s] = handler_fn
        else:
            handlers_by_selector[selector] = handler_fn
        return task

    return decorator


def skipping(selector):
    """
    The opposite of `excepting`.
    """

    def decorator(task):
        task_meta = _pire_meta(task)
        if _is_iterable(selector):
            task_meta['raising_classes'].update(selector)
        else:
            task_meta['raising_classes'].add(selector)
        return task

    return decorator


def finally_call(finally_handler):
    """
    `finally` meta key is created only if `finally_call` is used.
    """

    def decorator(task):
        task_meta = _pire_meta(task)
        task_meta['finally'] = finally_handler
        return task

    return decorator


def _matching_handler(handlers_by_selector, thrown_obj):
    """
    Matching `thrown_obj` with a handler is straightforward.
    `thrown_obj` is always a throwable thing, hence no check
    that selectors are subclasses of `Exception`.
    If nothing matches then so be it.
    """
    for selector, handler in handlers_by_selector.items():
        if isinstance(thrown_obj, selector):
            return handler


def _apply_handler(task_meta, thrown_obj, *args, **kwargs):
    """
    If a matching handler is found for `thrown_obj` and
    it's not supposed to be skipped then it gets called with
    a `thrown_obj` with the addition of the arguments passed
    to the original callable.

    Otherwise `False` is returned, which indicates that the exception
    should be raised after all.
    """
    handler = _matching_handler(task_meta['handlers_by_selector'], thrown_obj)
    skipped_selectors = task_meta['raising_classes']
    handler_skipped = any(isinstance(thrown_obj, i) for i in skipped_selectors)
    registered_and_not_skipped = handler and not handler_skipped
    if registered_and_not_skipped:
        handler(thrown_obj, *args, **kwargs)
    return registered_and_not_skipped


def _make_finally_call(task_meta, *args, **kwargs):
    """
    The return value from the `finally_handler` is ignored,
    otherwise it would be always returned instead of the result
    of the original callable.
    """
    if 'finally' in task_meta:
        task_meta.get('finally')(*args, **kwargs)


def supervise(task, *args, **kwargs):
    """
    A supervised call is really simple.
    `raise` is not in some `default_handler`, because
    apparently Python needs it to be in an `except` clause.
    """
    task_meta = _pire_meta(task)
    try:
        return task(*args, **kwargs)
    except Exception as thrown_obj:
        if not _apply_handler(task_meta, thrown_obj, *args, **kwargs):
            raise
    finally:
        _make_finally_call(task_meta, *args, **kwargs)


def supervised(fn):
    """
    This decorator replaces `fn` with a supervised call
    to `fn`.

    `wraps` copies all attributes from `fn`, but
    `supervise` is still being called on `fn`, so
    any copied meta information is deleted from `wrapper`.

    Meta information is lazily initialized, so if it's the
    only applied decorator then there is nothing to delete.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        return supervise(fn, *args, **kwargs)

    if hasattr(wrapper, _pire_attr):
        delattr(wrapper, _pire_attr)

    return wrapper

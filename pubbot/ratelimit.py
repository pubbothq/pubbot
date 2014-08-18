
from functools import wraps
import inspect

from django.core.cache import caches


def _get_key(fn, limit_by, *args, **kwargs):
    key = ['rate_limit']
    key.append(fn.__module__)
    key.append(fn.__name__)

    if limit_by:
        argspec = inspect.getargspec(fn)
        call_args = inspect.getcallargs(fn, *args, **kwargs)

        if argspec.varargs:
            del call_args[argspec.varargs]

        if argspec.keywords:
            keywords = call_args[argspec.keywords]
            del call_args[argspec.keywords]
            call_args.update(keywords)

        for arg in limit_by:
            key.append(call_args[arg])

    return ":".join(key)


def is_rate_limited(fn, limit_by=None, *args, **kwargs):
    key = _get_key(fn, limit_by, *args, **kwargs)

    key
    caches['default']

    return False


def track_rate_limit(rate, limit_by=None):
    def decorator(fn):
        @wraps(fn)
        def _inner(*args, **kwargs):
            if is_rate_limited(fn, limit_by, *args, **kwargs):
                kwargs = dict(kwargs)
                kwargs['rate_limited'] = True
            return fn(*args, **kwargs)
        return _inner
    return decorator


def enforce_rate_limit(rate, limit_by=None):
    def decorator(fn):
        @wraps(fn)
        def _inner(*args, **kwargs):
            if is_rate_limited(fn, limit_by, *args, **kwargs):
                return
            return fn(*args, **kwargs)
        return _inner
    return decorator

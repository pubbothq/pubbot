# Copyright 2014 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import wraps
import inspect
import time

from django.core.cache import caches


def _get_rate(rate):
    if "/" not in rate:
        raise ValueError("'%s' is not a valid rate." % rate)

    number, period = rate.split("/", 1)

    if period[-1] not in ('s', 'm', 'h', 'd'):
        raise ValueError("'%s' not recognised. Must be one of s, m, h or d." % period[-1])

    try:
        number = int(number)
    except ValueError:
        raise ValueError("Invalid frequency: '%s'" % number)

    period, units = period[:-1], period[-1]
    if period:
        try:
            period = int(period)
        except ValueError:
            raise ValueError("Invalid period: '%s'" % period)
    else:
        period = 1

    period = period * {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
    }[units]

    return number, period


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


def check_rate_limit(freq, period, fn, limit_by=None, *args, **kwargs):
    key = _get_key(fn, limit_by, *args, **kwargs)

    hits = caches['default'].get(key, [])

    now = time.time()
    while hits and (now - hits[0]) > period:
        hits.pop(0)

    hits.append(now)

    caches['default'].set(key, hits)

    return len(hits) > freq


def track_rate_limit(rate, limit_by=None):
    freq, period = _get_rate(rate)

    def decorator(fn):
        @wraps(fn)
        def _inner(*args, **kwargs):
            if check_rate_limit(freq, period, fn, limit_by, *args, **kwargs):
                kwargs = dict(kwargs)
                kwargs['rate_limited'] = True
            return fn(*args, **kwargs)
        return _inner
    return decorator


def enforce_rate_limit(rate, limit_by=None):
    freq, period = _get_rate(rate)

    def decorator(fn):
        @wraps(fn)
        def _inner(*args, **kwargs):
            if check_rate_limit(freq, period, fn, limit_by, *args, **kwargs):
                return
            return fn(*args, **kwargs)
        return _inner
    return decorator

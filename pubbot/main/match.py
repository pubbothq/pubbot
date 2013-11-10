# Copyright 2008-2013 the original author or authors
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

import re


def get_regex_for_routing_key(routing_key):
    regex = ['^']
    parts = routing_key.split(".")
    while parts:
        part = parts.pop(0)
        if part == '#':
            regex.append('[^.]+(\.[^.]+)*')
        elif part == '*':
            regex.append(r'[^.]+')
        else:
            regex.append(re.escape(part))
        regex.append(r'\.')
    regex[-1:] = [r'$']
    return re.compile(''.join(regex))


def get_regex_for_routing_keys(routing_keys):
    return [get_regex_for_routing_key(rk) for rk in routing_keys]


def match(routing_keys, msg):
    for expr in get_regex_for_routing_keys(routing_keys):
        if expr.match(msg):
            return True
    return False

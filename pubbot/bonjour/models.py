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

from django.db import models


class Device(models.Model):

    fullname = models.CharField(max_length=1024)
    host = models.CharField(max_length=1024)
    port = models.PositiveIntegerField(max_length=1024)
    txt = models.CharField(max_length=1024)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)


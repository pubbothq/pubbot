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

from django.db.backends.signals import connection_created


def setup_sqlite_connection(sender, connection, **kwargs):
    if connection.vendor != "sqlite":
        return

    cursor = connection.cursor()
    cursor.execute("PRAGMA journal_mode = truncate;")
    cursor.execute("PRAGMA temp_store = memory;")
    cursor.execute("PRAGMA synchronous = OFF;")

    cursor.execute("PRAGMA cache_size = 0;")
    cursor.execute("PRAGMA page_size = 4096;")


connection_created.connect(setup_sqlite_connection)

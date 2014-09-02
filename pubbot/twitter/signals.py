# Copyright 2014 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.dispatch import Signal

# User got a tweet appear in their timeline
tweet = Signal(signal_args=['screen_name', 'text'])

# User deauthorises stream
access_revoked = Signal()

# User is blocked, or user blocks someone
block = Signal()

# User is unblocked, or user unblocks someone
unblock = Signal()

# User favorites something, or a users tweet is favorited
favorite = Signal()

# User unfavorites something, or a users tweet is unfavorited
unfavorite = Signal()

# User follows someone, or is unfollowed
follow = Signal()

# User unfollows someone
unfollow = Signal()

list_created = Signal()

list_destroyed = Signal()

list_updated = Signal()

list_member_added = Signal()

list_member_removed = Signal()

list_user_subscribed = Signal()

list_user_unsubscribed = Signal()

user_update = Signal()

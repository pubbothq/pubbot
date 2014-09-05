# Copyright 2008-2013 the original author or authors
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

from pubbot.dispatch import Signal


# Triggered when a commit comment is created
commit_comment = Signal(providing_args=["payload"])

# Represents a created respository, branch or tag
create = Signal(providing_args=["payload"])

# Represents a deleted branch or tag
delete = Signal(providing_args=["payload"])

# Represents a deployent
deployment = Signal(providing_args=["payload"])
deployment_event = Signal(providing_args=["payload"])

# Triggered when a Wiki page is created or updated
gollum = Signal(providing_args=["payload"])

# Triggered when someone comments on an issue
issue_comment = Signal(providing_args=["payload"])

# Triggered when an issue is assigned, unassigned, labeled, unlabeled, opened, closed or reopned
issues = Signal(providing_args=["payload"])

# Triggered when a user is added as a collaborator
member = Signal(providing_args=["payload"])

# Triggered when a private repository is open sourced.
public = Signal(providing_args=["payload"])

# Triggered when a pull request is assigned, unassigned, labeled, unlabled, opened, closed, reopened or synchronized
pull_request = Signal(providing_args=["payload"])

# Triggered when a comment is created on a portion of the unified diff of a pull request
pull_request_review_comment = Signal(providing_args=["payload"])

# Triggered when somone pushes to a branch
push = Signal(providing_args=["payload"])

# Triggered when a release is published
release = Signal(providing_args=["payload"])

# Triggered when the status of a Git commit changes - For examplem, if CI passes or fails
status = Signal(providing_args=["payload"])

# Triggered when a user is added to a team or when a repo is added to a team
team_add = Signal(providing_args=["payload"])

# Triggered when a user stars a repo
watch = Signal(providing_args=["payload"])

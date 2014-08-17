# Copyright 2014 John Carr
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

import logging

from django.conf import settings
from django.utils.importlib import import_module
from django.utils.functional import LazyObject

from .service import BaseService


logger = logging.getLogger(__name__)


class PubbotService(BaseService):

    def __init__(self, name='pubbot'):
        super(PubbotService, self).__init__(name)

        for installed_app in settings.INSTALLED_APPS:
            self.logger.debug("Checking {installed_app} for receivers".format(installed_app=installed_app))
            try:
                import_module("%s.receivers" % installed_app)
            except ImportError as e:
                if str(e) != "No module named receivers":
                    self.logger.exception(e)

            self.logger.debug("Checking {installed_app} for Service".format(installed_app=installed_app))
            module_name = "%s.service" % installed_app
            try:
                module = import_module(module_name)
            except ImportError as e:
                if str(e) != "No module named service":
                    self.logger.exception(e)
                continue

            if hasattr(module, 'Service'):
                Service = getattr(module, 'Service')
                self.add_child(Service(name=installed_app))


class ConfiguredPubbotService(LazyObject):

    def _setup(self):
        self._wrapped = PubbotService()


bot = ConfiguredPubbotService()

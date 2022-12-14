# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyChoice
from service.models import Customer


class CustomerFactory(factory.Factory):
    """Creates fake Customers"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Customer

    id = factory.Sequence(lambda n: n)
    f_name = factory.Faker("name")
    l_name = factory.Faker("name")
    active = True
    name = FuzzyChoice(choices=["home", "work", "other"])
    street = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")
    postalcode = factory.Faker("postalcode")

"""
Test cases for Customer Model
"""
import logging
import os
import unittest

from service import app
from service.models import Customer, DataValidationError, PersistentBase, db
from tests.factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  Customer   M O D E L   T E S T   C A S E S
######################################################################
class TestCustomer(unittest.TestCase):      # pylint: disable=R0904
    """Test Cases for Customer Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Customer.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_init(self):
        """It should Create a base object with id None"""
        customer = PersistentBase()
        self.assertEqual(customer.id, None)

    def test_create_a_customer(self):
        """It should Create a Customer and assert that it exists"""
        fake_customer = CustomerFactory()
        # pylint: disable=unexpected-keyword-arg
        customer = Customer(
            f_name=fake_customer.f_name,
            l_name=fake_customer.l_name,
            active=fake_customer.active,
            name=fake_customer.name,
            street=fake_customer.street,
            city=fake_customer.city,
            state=fake_customer.state,
            postalcode=fake_customer.postalcode
        )
        self.assertIsNotNone(customer)
        self.assertEqual(customer.id, None)
        self.assertEqual(customer.f_name, fake_customer.f_name)
        self.assertEqual(customer.l_name, fake_customer.l_name)
        self.assertEqual(customer.active, fake_customer.active)

    def test_add_a_customer(self):
        """It should Create a customer and add it to the database"""
        customers = Customer.all()
        self.assertEqual(customers, [])
        customer = CustomerFactory()
        customer.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(customer.id)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)

    def test_read_customer(self):
        """It should Read a customer"""
        customer = CustomerFactory()
        customer.create()

        # Read it back
        found_customer = Customer.find(customer.id)
        self.assertEqual(found_customer.id, customer.id)
        self.assertEqual(found_customer.f_name, customer.f_name)
        self.assertEqual(found_customer.l_name, customer.l_name)
        self.assertEqual(found_customer.active, customer.active)
        self.assertEqual(found_customer.name, customer.name)
        self.assertEqual(found_customer.street, customer.street)
        self.assertEqual(found_customer.city, customer.city)
        self.assertEqual(found_customer.state, customer.state)
        self.assertEqual(found_customer.postalcode, customer.postalcode)

    def test_update_customer(self):
        """It should Update a customer"""
        customer = CustomerFactory(f_name="BobOne")
        customer.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.f_name, "BobOne")

        # Fetch it back
        customer = Customer.find(customer.id)
        customer.f_name = "BobTwo"
        customer.update()

        # Fetch it back again
        customer = Customer.find(customer.id)
        self.assertEqual(customer.f_name, "BobTwo")

    def test_delete_a_customer(self):
        """It should Delete a customer from the database"""
        customers = Customer.all()
        self.assertEqual(customers, [])
        customer = CustomerFactory()
        customer.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(customer.id)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        customer = customers[0]
        customer.delete()
        customers = Customer.all()
        self.assertEqual(len(customers), 0)

    def test_list_all_customers(self):
        """It should List all Customers in the database"""
        customers = Customer.all()
        self.assertEqual(customers, [])
        for customer in CustomerFactory.create_batch(5):
            customer.create()
        # Assert that there are not 5 customers in the database
        customers = Customer.all()
        self.assertEqual(len(customers), 5)

    def test_find_by_name(self):
        """It should Find a Customer by name"""
        customer = CustomerFactory()
        customer.create()

        # Fetch it back by name
        same = Customer.find_by_name(
            customer.f_name, customer.l_name
            )[0]
        self.assertEqual(same.id, customer.id)
        self.assertEqual(same.f_name, customer.f_name)
        self.assertEqual(same.l_name, customer.l_name)
        self.assertEqual(same.active, customer.active)

    def test_serialize_a_customer(self):
        """It should Serialize a Customer"""
        customer = CustomerFactory()
        serial_customer = customer.serialize()
        self.assertEqual(serial_customer["id"], customer.id)
        self.assertEqual(serial_customer["first_name"], customer.f_name)
        self.assertEqual(serial_customer["last_name"], customer.l_name)
        self.assertEqual(serial_customer["active"], customer.active)
        self.assertEqual(len(serial_customer["addresses"]), 1)
        addresses = serial_customer["addresses"]
        self.assertEqual(addresses[0]["name"], customer.name)
        self.assertEqual(addresses[0]["street"], customer.street)
        self.assertEqual(addresses[0]["city"], customer.city)
        self.assertEqual(addresses[0]["state"], customer.state)
        self.assertEqual(addresses[0]["postalcode"], customer.postalcode)

    def test_deserialize_a_customer(self):
        """It should Deserialize a customer"""
        customer = CustomerFactory()
        customer.create()
        serial_customer = customer.serialize()
        new_customer = Customer()
        new_customer.deserialize(serial_customer)
        self.assertEqual(new_customer.f_name, customer.f_name)
        self.assertEqual(new_customer.l_name, customer.l_name)
        self.assertEqual(new_customer.active, customer.active)

    def test_deserialize_a_customer_with_new_address_info(self):
        """It should Deserialize a customer with new address"""
        customer = CustomerFactory()
        customer.create()
        serial_customer = customer.serialize()
        serial_customer["addresses"][0]["street"] = "New Changed St"
        customer.deserialize(serial_customer)
        self.assertEqual(customer.street, "New Changed St")

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a customer with a KeyError"""
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize a customer with a TypeError"""
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, [])

    def test_update_customer_address(self):
        """It should Update a customers address"""
        customers = Customer.all()
        self.assertEqual(customers, [])

        customer = CustomerFactory()
        customer.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(customer.id)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)

        # Fetch it back
        customer = Customer.find(customer.id)
        old_city = customer.city
        print("%r", old_city)
        # Change the city
        customer.city = "XX"
        customer.update()

        # Fetch it back again
        customer = Customer.find(customer.id)
        self.assertEqual(customer.city, "XX")

    def test_deactivate_customer(self):
        """It should deactivate a customer"""
        customer = CustomerFactory()
        customer.create()
        # Assert that it was assigned active = True
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.active, True)

        # Fetch it back and deactivate
        customer = Customer.find(customer.id)
        customer.deactivate()
        customer.update()

        # Fetch it back again
        customer = Customer.find(customer.id)
        self.assertEqual(customer.active, False)

    def test_activate_customer(self):
        """It should activate a customer"""
        customer = CustomerFactory()
        customer.create()
        # Assert that it was assigned active = True
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.active, True)

        # Fetch it back and deactivate
        customer = Customer.find(customer.id)
        customer.deactivate()
        customer.update()

        # Fetch it back again
        customer = Customer.find(customer.id)
        self.assertEqual(customer.active, False)

        # Now reactivate it
        customer.activate()
        customer.update()

        # Fetch it back again
        customer = Customer.find(customer.id)
        self.assertEqual(customer.active, True)

    def test_find_by_activity(self):
        """It should Find Customers by Activity"""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        active = customers[0].active
        count = len(
            [customer for customer in customers if customer.active == active]
            )
        found = Customer.find_by_activity(active)
        self.assertEqual(found.count(), count)
        for customer in found:
            active_flag = customer.active
            self.assertEqual(customer.active, active_flag)

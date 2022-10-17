"""
Test cases for Customer Model
"""
import logging
import unittest
import os
from service import app


from service.models import Customer, Address, DataValidationError, db
from tests.factories import CustomerFactory, AddressFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  Customer   M O D E L   T E S T   C A S E S
######################################################################
class TestCustomer(unittest.TestCase):
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

    def test_create_a_customer(self):
        """It should Create a Customer and assert that it exists"""
        fake_customer = CustomerFactory()
        # pylint: disable=unexpected-keyword-arg
        customer = Customer(
            f_name = fake_customer.f_name,
            l_name = fake_customer.l_name,
            active = fake_customer.active,
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
        self.assertEqual(found_customer.addresses, [])

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
        same_customer = Customer.find_by_name(customer.f_name, customer.l_name)[0]
        self.assertEqual(same_customer.id, customer.id)
        self.assertEqual(same_customer.f_name, customer.f_name)
        self.assertEqual(same_customer.l_name, customer.l_name)
        self.assertEqual(same_customer.active, customer.active)

    def test_serialize_a_customer(self):
        """It should Serialize a Customer"""
        customer = CustomerFactory()
        address = AddressFactory()
        customer.addresses.append(address)
        serial_customer = customer.serialize()
        self.assertEqual(serial_customer["id"], customer.id)
        self.assertEqual(serial_customer["f_name"], customer.f_name)
        self.assertEqual(serial_customer["l_name"], customer.l_name)
        self.assertEqual(serial_customer["active"], customer.active)
        self.assertEqual(len(serial_customer["addresses"]), 1)
        addresses = serial_customer["addresses"]
        self.assertEqual(addresses[0]["id"], address.id)
        self.assertEqual(addresses[0]["customer_id"], address.customer_id)
        self.assertEqual(addresses[0]["name"], address.name)
        self.assertEqual(addresses[0]["street"], address.street)
        self.assertEqual(addresses[0]["city"], address.city)
        self.assertEqual(addresses[0]["state"], address.state)
        self.assertEqual(addresses[0]["postalcode"], address.postalcode)

    def test_deserialize_a_customer(self):
        """It should Deserialize a customer"""
        customer = CustomerFactory()
        customer.addresses.append(AddressFactory())
        customer.create()
        serial_customer = customer.serialize()
        new_customer = Customer()
        new_customer.deserialize(serial_customer)
        self.assertEqual(new_customer.f_name, customer.f_name)
        self.assertEqual(new_customer.l_name, customer.l_name)
        self.assertEqual(new_customer.active, customer.active)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a customer with a KeyError"""
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize a customer with a TypeError"""
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, [])

    def test_deserialize_address_key_error(self):
        """It should not Deserialize an address with a KeyError"""
        address = Address()
        self.assertRaises(DataValidationError, address.deserialize, {})

    def test_deserialize_address_type_error(self):
        """It should not Deserialize an address with a TypeError"""
        address = Address()
        self.assertRaises(DataValidationError, address.deserialize, [])

    def test_add_customer_address(self):
        """It should Create a customer with an address and add it to the database"""
        customers = Customer.all()
        self.assertEqual(customers, [])
        customer = CustomerFactory()
        address = AddressFactory(customer=customer)
        customer.addresses.append(address)
        customer.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(customer.id)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)

        new_customer = Customer.find(customer.id)
        self.assertEqual(new_customer.addresses[0].name, address.name)

        address2 = AddressFactory(customer=customer)
        customer.addresses.append(address2)
        customer.update()

        new_customer = Customer.find(customer.id)
        self.assertEqual(len(new_customer.addresses), 2)
        self.assertEqual(new_customer.addresses[1].name, address2.name)

    def test_update_customer_address(self):
        """It should Update a customers address"""
        customers = Customer.all()
        self.assertEqual(customers, [])

        customer = CustomerFactory()
        address = AddressFactory(customer=customer)
        customer.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(customer.id)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)

        # Fetch it back
        customer = Customer.find(customer.id)
        old_address = customer.addresses[0]
        print("%r", old_address)
        self.assertEqual(old_address.city, address.city)
        # Change the city
        old_address.city = "XX"
        customer.update()

        # Fetch it back again
        customer = Customer.find(customer.id)
        address = customer.addresses[0]
        self.assertEqual(address.city, "XX")

    def test_delete_customer_address(self):
        """It should Delete a customer address"""
        customers = Customer.all()
        self.assertEqual(customers, [])

        customer = CustomerFactory()
        address = AddressFactory(customer=customer)
        customer.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(customer.id)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)

        # Fetch it back
        customer = Customer.find(customer.id)
        address = customer.addresses[0]
        address.delete()
        customer.update()

        # Fetch it back again
        customer = Customer.find(customer.id)
        self.assertEqual(len(customer.addresses), 0)
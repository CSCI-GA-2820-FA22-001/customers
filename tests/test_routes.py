"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import logging
import os
from unittest import TestCase

from service import app
from service.common import status  # HTTP Status Codes
from service.models import Customer, db, init_db
from tests.factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=R0904
class TestYourCustomerServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_customers(self, count):
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            print(test_customer)
            response = self.client.post(BASE_URL, json=test_customer.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test customer"
            )

            print(test_customer)
            new_customer = response.get_json()
            test_customer.id = new_customer["id"]
            customers.append(test_customer)
        return customers

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # data = resp.get_json()
        # self.assertEqual(data["name"], "Customer Demo REST API Service")

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "OK")

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_customer(self):
        """It should Create a new Customer"""
        test_customer = CustomerFactory()
        logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["first_name"], test_customer.f_name)
        self.assertEqual(new_customer["last_name"], test_customer.l_name)
        self.assertEqual(new_customer["active"], test_customer.active)
        # self.assertEqual(new_customer["addresses"], test_customer.addresses.id)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_customer = response.get_json()
        self.assertEqual(new_customer["first_name"], test_customer.f_name)
        self.assertEqual(new_customer["last_name"], test_customer.l_name)
        self.assertEqual(new_customer["active"], test_customer.active)
        # self.assertEqual(new_customer["addresses"], test_customer.addresses.id)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_customer(self):
        """It should Get a single Customer"""
        # get the id of a customer
        test_customer = self._create_customers(1)[0]
        resp = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["first_name"], test_customer.f_name)
        self.assertEqual(data["last_name"], test_customer.l_name)
        self.assertEqual(data["active"], test_customer.active)

    def test_get_customer_not_found(self):
        """It should not Get a Customer thats not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_customer(self):
        """It should Delete a customer"""
        test_customer = self._create_customers(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_list_all_customer(self):
        """It should list all Customers"""
        self._create_customers(5)
        # test_customer = self._create_customers(5)[0]
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 5)
        logging.debug("Response data = %s", data)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_customer(self):
        """It should Update an existing Customer"""
        # create a Customer to update
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = response.get_json()
        logging.debug(new_customer)
        # new_customer["category"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_customer['id']}", json=new_customer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # updated_customer = response.get_json()
        # self.assertEqual(updated_customer["category"], "unknown")
        
    def test_update_customer_and_address(self):
        """It should Update an existing Customer"""
        # create a Customer to update
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = response.get_json()
        print("customer info is ", new_customer)
        logging.debug(new_customer)
        # new_customer["category"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_customer['id']}", json=new_customer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # updated_customer = response.get_json()
        # self.assertEqual(updated_customer["category"], "unknown")

    

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################
    def test_bad_request(self):
        """It should not allow bad request"""
        response = self.client.post(BASE_URL, json={"name": " "})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_http_request(self):
        """It should not allow unsupported HTTP methods"""
        response = self.client.patch(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_customer_no_content_type(self):
        """It should not Create a Customer with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_bad_content_type(self):
        """It should not Create a Customer with bad content type"""
        response = self.client.post(BASE_URL, headers={'Content-Type': 'notJSON'})
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_customer_not_found(self):
        """It should not Update a Customer who doesn't exist"""
        response = self.client.put(f"{BASE_URL}/0", json={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_customer_not_found(self):
        """It should not activate a Customer who doesn't exist"""
        response = self.client.put(f"{BASE_URL}/0/activate", json={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_customer_not_found(self):
        """It should not activate a Customer who doesn't exist"""
        response = self.client.put(f"{BASE_URL}/0/deactivate", json={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  T E S T   Q U E R Y   S T R I N G S
    ######################################################################
    def test_query_customers_by_activity(self):
        """It should Query Customers by Activity"""
        customers = self._create_customers(10)
        test_active = customers[0].active
        active_list = [customer for customer in customers if customer.active == test_active]
        logging.info(
            "Active=%s: %d = %s", test_active, len(active_list), active_list
        )
        resp = self.client.get(BASE_URL, query_string=f"active={str(test_active)}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(active_list))
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["active"], test_active)

    def test_deactivate_customer(self):
        """It should deactivate an existing Customer"""

        # create a new customer then deactivate it
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # deactivate one customer
        new_customer = response.get_json()
        response = self.client.put(f"{BASE_URL}/{new_customer['id']}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        logging.debug(new_customer)
        new_customer = response.get_json()
        self.assertEqual(new_customer["active"], False)

    def test_activate_customer(self):
        """It should activate an existing Customer"""

        # create a new customer then deactivate it
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # deactivate one customer
        new_customer = response.get_json()
        response = self.client.put(f"{BASE_URL}/{new_customer['id']}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        logging.debug(new_customer)
        new_customer = response.get_json()
        self.assertEqual(new_customer["active"], False)

        # now activate this customer again
        response = self.client.put(f"{BASE_URL}/{new_customer['id']}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        logging.debug(new_customer)
        new_customer = response.get_json()
        self.assertEqual(new_customer["active"], True)

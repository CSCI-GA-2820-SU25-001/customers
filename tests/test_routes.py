######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
######################################################################

"""
TestCustomer API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from urllib.parse import quote_plus
from service.common import status
from unittest.mock import patch, MagicMock
from service.common import status
from service.models import db, Customer
from .factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create customers
    ############################################################
    def _create_customers(self, count: int = 1) -> list:
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            response = self.client.post(BASE_URL, json=test_customer.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test customer",
            )
            new_customer = response.get_json()
            test_customer.id = new_customer["id"]
            customers.append(test_customer)
        return customers

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page and return root metadata"""  # root metadata is all the endpoints at the bottom
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Customer REST API Service")

        self.assertIn("version", data)
        self.assertIn("paths", data)

        # Added in add-route-route issue: check that all key endpoints exist
        self.assertIn("create", data["paths"])
        self.assertIn("list_all", data["paths"])
        self.assertIn("read_one", data["paths"])
        self.assertIn("update", data["paths"])
        self.assertIn("delete", data["paths"])
        self.assertIn("find_by_email", data["paths"])

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        self._create_customers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------

    def test_get_customer_exists(self):
        """It should read a customer that exists"""
        test_customer = self._create_customers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["first_name"], test_customer.first_name)
        self.assertEqual(data["last_name"], test_customer.last_name)

    def test_get_customer_not_exist(self):
        """It should return a False assertion for finding a customer that doesn't exist"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

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
        self.assertEqual(new_customer["first_name"], test_customer.first_name)
        self.assertEqual(new_customer["last_name"], test_customer.last_name)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["phone_number"], test_customer.phone_number)
        self.assertEqual(new_customer["email"], test_customer.email)

        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_customer = response.get_json()
        self.assertEqual(new_customer["first_name"], test_customer.first_name)
        self.assertEqual(new_customer["last_name"], test_customer.last_name)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["phone_number"], test_customer.phone_number)
        self.assertEqual(new_customer["email"], test_customer.email)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_customer(self):
        """It should Update an existing Customer"""
        # create a customer to update
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_customer = response.get_json()
        logging.debug(new_customer)
        new_customer["first_name"] = "Updated"
        response = self.client.put(
            f"{BASE_URL}/{new_customer['id']}", json=new_customer
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_customer = response.get_json()
        self.assertEqual(updated_customer["first_name"], "Updated")

    def test_update_customer_not_found(self):
        """It should return 404 when updating non-existent customer"""
        customer_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
        }
        response = self.client.put(f"{BASE_URL}/999", json=customer_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_customer(self):
        """It should Delete a Customer"""
        test_customer = self._create_customers(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_customer(self):
        """It should Delete a Customer even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------
    def test_query_by_email(self):
        """It should Query Customers by email"""
        customers = self._create_customers(3)
        test_email = customers[0].email
        response = self.client.get(
            BASE_URL, query_string=f"email={quote_plus(test_email)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["email"], test_email)

    def test_query_by_email_not_found(self):
        """It should return empty list for non-existent email"""
        response = self.client.get(BASE_URL, query_string="email=notfound@example.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_customer_missing_each_required_field(self):
        """It should return 400 if any required field is missing"""
        # This simulates a client sending a request with missing input.
        # In this case, we remove each required field one at a time to mimic a
        # user or frontend accidentally omitting a required field from the JSON body.
        # This helps verify that the API returns a 400 error instead of crashing or silently failing.
        required_fields = ["first_name", "last_name", "email"]
        for field in required_fields:
            with self.subTest(field=field):
                customer = CustomerFactory().serialize()
                del customer[field]
                response = self.client.post(BASE_URL, json=customer)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    def test_create_customer_no_content_type(self):
        """It should not Create a Customer with no Content-Type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_wrong_content_type(self):
        """It should not Create a Pet with the wrong content type"""
        # Set wrong content type (text/html)
        response = self.client.post(
            BASE_URL, data="Not valid JSON", content_type="text/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_customer_no_content_type(self):
        """It should not Update a Customer with no Content-Type"""
        response = self.client.put(f"{BASE_URL}/1")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_customer_wrong_content_type(self):
        """It should not Update a Customer with wrong content type"""
        response = self.client.put(
            f"{BASE_URL}/1", data="Not JSON", content_type="text/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_customer_bad_data(self):
        """It should not Update a Customer with bad data"""
        test_customer = self._create_customers(1)[0]
        # Send invalid JSON (missing required fields)
        bad_data = {"first_name": "Updated"}  # Missing last_name and email
        response = self.client.put(f"{BASE_URL}/{test_customer.id}", json=bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

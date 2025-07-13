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
from urllib.parse import quote_plus
from unittest import TestCase
from wsgi import app
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
        self.assertIn("create", data["paths"])
        self.assertIn("list_all", data["paths"])
        self.assertIn("read_one", data["paths"])
        self.assertIn("update", data["paths"])
        self.assertIn("delete", data["paths"])
        self.assertIn("find_by_email", data["paths"])
        self.assertIn("suspend", data["paths"])
        self.assertIn("activate", data["paths"])

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

    def test_query_by_first_name(self):
        """It should Query Customers by first name"""
        customers = self._create_customers(5)
        test_first_name = customers[0].first_name
        response = self.client.get(
            BASE_URL, query_string=f"first_name={quote_plus(test_first_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
        for customer in data:
            self.assertEqual(customer["first_name"], test_first_name)

    def test_query_by_last_name(self):
        """It should Query Customers by last name"""
        customers = self._create_customers(5)
        test_last_name = customers[0].last_name
        response = self.client.get(
            BASE_URL, query_string=f"last_name={quote_plus(test_last_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
        for customer in data:
            self.assertEqual(customer["last_name"], test_last_name)

    def test_query_by_phone_number(self):
        """It should Query Customers by phone number"""
        customers = self._create_customers(3)
        test_phone = customers[0].phone_number
        response = self.client.get(
            BASE_URL, query_string=f"phone_number={quote_plus(test_phone)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["phone_number"], test_phone)

    def test_query_by_multiple_parameters(self):
        """It should Query Customers by multiple parameters"""
        customers = self._create_customers(5)
        test_customer = customers[0]
        query_string = f"first_name={quote_plus(test_customer.first_name)}&last_name={quote_plus(test_customer.last_name)}"
        response = self.client.get(BASE_URL, query_string=query_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
        # Check that all returned customers match both criteria
        for customer in data:
            self.assertEqual(customer["first_name"], test_customer.first_name)
            self.assertEqual(customer["last_name"], test_customer.last_name)

    def test_query_email_and_first_name_combined(self):
        """It should Query Customers by email and first name combined"""
        customers = self._create_customers(3)
        test_customer = customers[0]
        query_string = f"email={quote_plus(test_customer.email)}&first_name={quote_plus(test_customer.first_name)}"
        response = self.client.get(BASE_URL, query_string=query_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["email"], test_customer.email)
        self.assertEqual(data[0]["first_name"], test_customer.first_name)

    def test_query_all_parameters_combined(self):
        """It should Query Customers by all parameters combined"""
        customers = self._create_customers(3)
        test_customer = customers[0]
        query_string = (
            f"first_name={quote_plus(test_customer.first_name)}&"
            f"last_name={quote_plus(test_customer.last_name)}&"
            f"email={quote_plus(test_customer.email)}&"
            f"phone_number={quote_plus(test_customer.phone_number)}"
        )
        response = self.client.get(BASE_URL, query_string=query_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], test_customer.first_name)
        self.assertEqual(data[0]["last_name"], test_customer.last_name)
        self.assertEqual(data[0]["email"], test_customer.email)
        self.assertEqual(data[0]["phone_number"], test_customer.phone_number)

    def test_query_by_suspended_true(self):
        """It should Query Customers that are suspended"""
        customers = self._create_customers(3)
        response = self.client.put(f"{BASE_URL}/{customers[0].id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(BASE_URL, query_string="suspended=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertTrue(data[0]["suspended"])
        self.assertEqual(data[0]["id"], customers[0].id)

    def test_query_by_suspended_false(self):
        """It should Query Customers that are not suspended"""
        customers = self._create_customers(3)
        response = self.client.put(f"{BASE_URL}/{customers[1].id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(BASE_URL, query_string="suspended=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        for customer in data:
            self.assertFalse(customer["suspended"])

    def test_query_by_suspended_with_other_parameters(self):
        """It should Query Customers by suspended status combined with other filters"""
        customers = self._create_customers(3)
        test_customer = customers[0]

        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        query_string = f"first_name={quote_plus(test_customer.first_name)}&suspended=true"
        response = self.client.get(BASE_URL, query_string=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], test_customer.first_name)
        self.assertTrue(data[0]["suspended"])

    def test_query_suspended_boolean_variations(self):
        """It should handle various boolean representations for suspended parameter"""
        customers = self._create_customers(2)
        response = self.client.put(f"{BASE_URL}/{customers[0].id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for true_value in ['true', 'True', '1']:
            response = self.client.get(BASE_URL, query_string=f"suspended={true_value}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertEqual(len(data), 1)
            self.assertTrue(data[0]["suspended"])

        for false_value in ['false', 'False', '0']:
            response = self.client.get(BASE_URL, query_string=f"suspended={false_value}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertEqual(len(data), 1)
            self.assertFalse(data[0]["suspended"])

    # ----------------------------------------------------------
    # TEST SUSPEND CUSTOMER
    # ----------------------------------------------------------

    def test_suspend_customer_success(self):
        """It should suspend a customer successfully"""
        test_customer = self._create_customers(1)[0]
        # Ensure not suspended initially
        self.assertFalse(
            test_customer.suspended if hasattr(test_customer, "suspended") else False
        )
        # Suspend the customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(data["suspended"])
        # Fetch again to confirm in DB
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(data["suspended"])

    def test_suspend_customer_not_found(self):
        """It should return 404 when suspending a non-existent customer"""
        response = self.client.put(f"{BASE_URL}/99999/suspend")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_suspend_customer_already_suspended(self):
        """It should allow suspending an already suspended customer (idempotent)"""
        test_customer = self._create_customers(1)[0]
        # Suspend once
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Suspend again
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(data["suspended"])

    def test_suspend_customer_wrong_method(self):
        """It should not allow GET or POST on suspend endpoint"""
        test_customer = self._create_customers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ----------------------------------------------------------
    # TEST ACTIVATE CUSTOMER
    # ----------------------------------------------------------
    def test_activate_customer_success(self):
        """It should activate (unsuspend) a customer successfully"""
        test_customer = self._create_customers(1)[0]
        # Suspend the customer first
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Activate the customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertFalse(data["suspended"])
        # Fetch again to confirm in DB
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertFalse(data["suspended"])

    def test_activate_customer_not_found(self):
        """It should return 404 when activating a non-existent customer"""
        response = self.client.put(f"{BASE_URL}/99999/activate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_activate_customer_already_active(self):
        """It should allow activating an already active customer (idempotent)"""
        test_customer = self._create_customers(1)[0]
        # Activate (should already be active)
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertFalse(data["suspended"])

    def test_activate_customer_wrong_method(self):
        """It should not allow GET or POST on activate endpoint"""
        test_customer = self._create_customers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post(f"{BASE_URL}/{test_customer.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ----------------------------------------------------------
    # TEST SERIALIZATION
    # ----------------------------------------------------------
    def test_get_customer_includes_suspended_field(self):
        """It should include suspended field in customer response"""
        test_customer = self._create_customers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()

        # Check that suspended field is present
        self.assertIn("suspended", data)
        self.assertIsInstance(data["suspended"], bool)
        # By default, customers should not be suspended
        self.assertFalse(data["suspended"])

    def test_list_customers_includes_suspended_field(self):
        """It should include suspended field in list customers response"""
        self._create_customers(3)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()

        # Check that all customers have suspended field
        for customer in data:
            self.assertIn("suspended", customer)
            self.assertIsInstance(customer["suspended"], bool)

    def test_create_customer_includes_suspended_field(self):
        """It should include suspended field in create customer response"""
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        self.assertIn("suspended", data)
        self.assertIsInstance(data["suspended"], bool)
        # New customers should default to not suspended
        self.assertFalse(data["suspended"])

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

    def test_query_by_first_name_not_found(self):
        """It should return empty list for non-existent first name"""
        # Create some customers but search for a name that doesn't exist
        self._create_customers(3)
        fake_name = CustomerFactory().first_name + "_NONEXISTENT"
        response = self.client.get(
            BASE_URL, query_string=f"first_name={quote_plus(fake_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_last_name_not_found(self):
        """It should return empty list for non-existent last name"""
        # Create some customers but search for a name that doesn't exist
        self._create_customers(3)
        fake_name = CustomerFactory().last_name + "_NONEXISTENT"
        response = self.client.get(
            BASE_URL, query_string=f"last_name={quote_plus(fake_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_phone_number_not_found(self):
        """It should return empty list for non-existent phone number"""
        # Create some customers but search for a phone that doesn't exist
        self._create_customers(3)
        fake_phone = CustomerFactory().phone_number + "999"
        response = self.client.get(
            BASE_URL, query_string=f"phone_number={quote_plus(fake_phone)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_with_multiple_parameters_not_found(self):
        """It should return empty list when multiple parameters don't match"""
        # Create some customers but search for combination that doesn't exist
        self._create_customers(3)
        fake_first = CustomerFactory().first_name + "_FAKE"
        fake_last = CustomerFactory().last_name + "_FAKE"
        query_string = (
            f"first_name={quote_plus(fake_first)}&last_name={quote_plus(fake_last)}"
        )
        response = self.client.get(BASE_URL, query_string=query_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_with_partial_match_not_found(self):
        """It should return empty list when only some parameters match"""
        customers = self._create_customers(2)
        test_customer = customers[0]
        # Use real first name but faker-generated fake last name
        fake_last_name = CustomerFactory().last_name + "_NOMATCH"
        query_string = f"first_name={quote_plus(test_customer.first_name)}&last_name={quote_plus(fake_last_name)}"
        response = self.client.get(BASE_URL, query_string=query_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_email_and_phone_mismatch(self):
        """It should return empty list when email and phone don't belong to same customer"""
        customers = self._create_customers(2)
        customer1 = customers[0]
        customer2 = customers[1]
        # Use email from customer1 and phone from customer2 - should find nothing
        query_string = f"email={quote_plus(customer1.email)}&phone_number={quote_plus(customer2.phone_number)}"
        response = self.client.get(BASE_URL, query_string=query_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_with_empty_parameter_values(self):
        """It should handle empty query parameter values"""
        # Create some customers first
        customers_created = self._create_customers(3)
        response = self.client.get(BASE_URL, query_string="first_name=&last_name=")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # Should return all customers since empty parameters are ignored
        self.assertEqual(len(data), len(customers_created))

    def test_query_with_url_encoded_special_names(self):
        """It should handle URL-encoded names with spaces correctly"""
        # Create a customer using factory data and modify to ensure it has special characters
        customer = CustomerFactory()
        base_name = customer.first_name
        # Create a name with space using factory base + modification
        customer.first_name = f"{base_name} Test"  # Factory name + space + Test
        response = self.client.post(BASE_URL, json=customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Query using URL encoding for the space
        test_name = customer.first_name  # Use the actual name we just created
        response = self.client.get(
            BASE_URL, query_string=f"first_name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], test_name)

    def test_query_with_url_encoded_last_name_spaces(self):
        """It should handle URL-encoded last names with spaces correctly"""
        # Test with last name containing spaces using factory data
        customer = CustomerFactory()
        base_last_name = customer.last_name
        # Create a last name with space using factory base
        customer.last_name = f"{base_last_name} III"  # Factory name + space + suffix
        response = self.client.post(BASE_URL, json=customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_name = customer.last_name
        response = self.client.get(
            BASE_URL, query_string=f"last_name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["last_name"], test_name)

    def test_query_by_suspended_no_matches(self):
        """It should return empty list when no customers match suspended status"""
        # Create customers (all active by default)
        self._create_customers(3)

        # Query for suspended customers (should be none)
        response = self.client.get(BASE_URL, query_string="suspended=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_suspended_with_nonmatching_other_params(self):
        """It should return empty when suspended status matches but other params don't"""
        customers = self._create_customers(2)
        # Suspend one customer
        response = self.client.put(f"{BASE_URL}/{customers[0].id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Query for suspended=true but with wrong first name
        fake_name = CustomerFactory().first_name + "_FAKE"
        query_string = f"suspended=true&first_name={quote_plus(fake_name)}"
        response = self.client.get(BASE_URL, query_string=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_suspended_all_parameters_combined(self):
        """It should Query by suspended status with all other parameters"""
        customers = self._create_customers(2)
        test_customer = customers[0]

        # Suspend the customer
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Query with ALL parameters including suspended
        query_string = (
            f"first_name={quote_plus(test_customer.first_name)}&"
            f"last_name={quote_plus(test_customer.last_name)}&"
            f"email={quote_plus(test_customer.email)}&"
            f"phone_number={quote_plus(test_customer.phone_number)}&"
            f"suspended=true"
        )
        response = self.client.get(BASE_URL, query_string=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], test_customer.first_name)
        self.assertEqual(data[0]["last_name"], test_customer.last_name)
        self.assertEqual(data[0]["email"], test_customer.email)
        self.assertEqual(data[0]["phone_number"], test_customer.phone_number)
        self.assertTrue(data[0]["suspended"])

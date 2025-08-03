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
from service.models import db, Customer, DataValidationError
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
        db.session.query(Customer).delete()
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
    def test_health_check(self):
        """It should return healthy status for /health endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_index(self):
        """It should return the index.html for / endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Customer Administration", response.data)

    def test_api_metadata(self):
        """It should return API metadata for /api endpoint"""
        response = self.client.get("/api")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIn("name", data)
        self.assertIn("paths", data)

    def test_data_validation_error_handler(self):
        """It should trigger DataValidationError handler and return 400"""
        # Instead of registering a new route, directly call the error handler
        from service.routes import handle_data_validation_error
        with app.test_request_context():
            response, code = handle_data_validation_error(DataValidationError("Test error message"))
            self.assertEqual(code, status.HTTP_400_BAD_REQUEST)
            data = response.get_json()
            self.assertIn("error", data)
            self.assertEqual(data["error"], "Test error message")

    def test_home_page_serves_html(self):
        """It should call the home page and return HTML"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.content_type, "text/html; charset=utf-8")
        self.assertIn(b"Customer Administration", resp.data)

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

        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

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
        query_string = (
            f"first_name={quote_plus(test_customer.first_name)}&"
            f"last_name={quote_plus(test_customer.last_name)}"
        )
        response = self.client.get(BASE_URL, query_string=query_string)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
        for customer in data:
            self.assertEqual(customer["first_name"], test_customer.first_name)
            self.assertEqual(customer["last_name"], test_customer.last_name)

    def test_query_email_and_first_name_combined(self):
        """It should Query Customers by email and first name combined"""
        customers = self._create_customers(3)
        test_customer = customers[0]
        query_string = (
            f"email={quote_plus(test_customer.email)}&"
            f"first_name={quote_plus(test_customer.first_name)}"
        )
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

        query_string = (
            "first_name=NonExistent&"
            "suspended=true"
        )
        response = self.client.get(BASE_URL, query_string=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

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
        self.assertFalse(
            test_customer.suspended if hasattr(test_customer, "suspended") else False
        )
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(data["suspended"])
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
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertFalse(data["suspended"])
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
        """It should allow activating an already active customer"""
        test_customer = self._create_customers(1)[0]
        # Ensure not suspended initially
        self.assertFalse(
            test_customer.suspended if hasattr(test_customer, "suspended") else False
        )
        # Activate once (should already be active)
        response = self.client.put(f"{BASE_URL}/{test_customer.id}/activate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertFalse(data["suspended"])
        # Activate again
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
    # TEST CONTENT TYPE AND MISSING DATA
    # ----------------------------------------------------------
    def test_create_customer_no_content_type(self):
        """It should not Create a Customer with no Content-Type"""
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_wrong_content_type(self):
        """It should not Create a Pet with the wrong content type"""
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize(), headers={"Content-Type": "application/xml"})
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_bad_data(self):
        """It should return 400 if any required field is missing"""
        test_customer = CustomerFactory()
        data = test_customer.serialize()
        del data["first_name"]
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_no_content_type(self):
        """It should not Update a Customer with no Content-Type"""
        test_customer = self._create_customers(1)[0]
        response = self.client.put(f"{BASE_URL}/{test_customer.id}", data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_customer_wrong_content_type(self):
        """It should not Update a Customer with wrong content type"""
        test_customer = self._create_customers(1)[0]
        response = self.client.put(f"{BASE_URL}/{test_customer.id}",
                                   json={"first_name": "New Name"}, headers={"Content-Type": "application/xml"})
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_customer_bad_data(self):
        """It should not Update a Customer with bad data"""
        test_customer = self._create_customers(1)[0]
        data = {"invalid_field": "some_value"}
        response = self.client.put(f"{BASE_URL}/{test_customer.id}", json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_by_first_name_not_found(self):
        """It should return empty list for non-existent first name"""
        response = self.client.get(BASE_URL, query_string="first_name=NonExistent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_last_name_not_found(self):
        """It should return empty list for non-existent last name"""
        response = self.client.get(BASE_URL, query_string="last_name=NonExistent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_by_phone_number_not_found(self):
        """It should return empty list for non-existent phone number"""
        response = self.client.get(BASE_URL, query_string="phone_number=999-999-9999")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_suspended_no_match(self):
        """It should return empty list when no customers match suspended status"""
        self._create_customers(3)
        response = self.client.get(BASE_URL, query_string="suspended=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_suspended_status_no_other_params_match(self):
        """It should return empty when suspended status matches but other params don't"""
        customers = self._create_customers(1)
        response = self.client.put(f"{BASE_URL}/{customers[0].id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        query_string = (
            "first_name=NonExistent&"
            "suspended=true"
        )
        response = self.client.get(BASE_URL, query_string=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_multiple_params_no_match(self):
        """It should return empty list when multiple parameters don't match"""
        self._create_customers(1)
        query_string = "first_name=Alice&last_name=Bob"
        response = self.client.get(BASE_URL, query_string=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_some_params_no_match(self):
        """It should return empty list when only some parameters match"""
        customer = self._create_customers(1)[0]
        query_string = (
            f"first_name={quote_plus(customer.first_name)}&"
            "email=wrong@example.com"
        )
        response = self.client.get(BASE_URL, query_string=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_query_url_encoded_names(self):
        """It should handle URL-encoded names with spaces correctly"""
        customer_data = CustomerFactory(first_name="First Name", last_name="Last Name")
        self.client.post(BASE_URL, json=customer_data.serialize())

        encoded_first_name = quote_plus("First Name")
        response = self.client.get(BASE_URL, query_string=f"first_name={encoded_first_name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["first_name"], "First Name")

    def test_query_url_encoded_last_names(self):
        """It should handle URL-encoded last names with spaces correctly"""
        customer_data = CustomerFactory(first_name="First", last_name="Last Name")
        self.client.post(BASE_URL, json=customer_data.serialize())

        encoded_last_name = quote_plus("Last Name")
        response = self.client.get(BASE_URL, query_string=f"last_name={encoded_last_name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["last_name"], "Last Name")

    def test_handle_empty_query_parameter_values(self):
        """It should handle empty query parameter values"""
        self._create_customers(1)
        response = self.client.get(BASE_URL, query_string="first_name=&email=")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)

    def test_error_handlers(self):
        """It should trigger all custom error handlers in error_handlers.py"""
        from service.common import error_handlers
        with app.test_request_context():
            # 400 Bad Request
            resp, code = error_handlers.bad_request(Exception("bad req"))
            self.assertEqual(code, 400)
            data = resp.get_json()
            self.assertEqual(data["error"], "Bad Request")
            self.assertIn("bad req", data["message"])

            # 404 Not Found
            resp, code = error_handlers.not_found(Exception("not found"))
            self.assertEqual(code, 404)
            data = resp.get_json()
            self.assertEqual(data["error"], "Not Found")
            self.assertIn("not found", data["message"])

            # 405 Method Not Allowed
            resp, code = error_handlers.method_not_supported(Exception("not allowed"))
            self.assertEqual(code, 405)
            data = resp.get_json()
            self.assertEqual(data["error"], "Method not Allowed")
            self.assertIn("not allowed", data["message"])

            # 415 Unsupported Media Type
            resp, code = error_handlers.mediatype_not_supported(Exception("unsupported media"))
            self.assertEqual(code, 415)
            data = resp.get_json()
            self.assertEqual(data["error"], "Unsupported media type")
            self.assertIn("unsupported media", data["message"])

            # 500 Internal Server Error
            resp, code = error_handlers.internal_server_error(Exception("server error"))
            self.assertEqual(code, 500)
            data = resp.get_json()
            self.assertEqual(data["error"], "Internal Server Error")
            self.assertIn("server error", data["message"])

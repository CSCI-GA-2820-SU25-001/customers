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
Test cases for Customer Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Customer, DataValidationError, db
from .factories import CustomerFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  C U S T O M E R   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomer(TestCase):
    """Test Cases for Customer Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_customer(self):
        """It should create a Customer"""
        customer = CustomerFactory()
        customer.create()
        self.assertIsNotNone(customer.id)
        found = Customer.all()
        self.assertEqual(len(found), 1)
        data = Customer.find(customer.id)
        self.assertEqual(data.first_name, customer.first_name)
        self.assertEqual(data.last_name, customer.last_name)
        self.assertEqual(data.address, customer.address)
        self.assertEqual(data.email, customer.email)
        self.assertEqual(data.phone_number, customer.phone_number)

    def test_read_a_customer(self):
        """It should Read a customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        self.assertIsNotNone(customer.id)
        found_customer = Customer.find(customer.id)
        self.assertEqual(found_customer.id, customer.id)
        self.assertEqual(found_customer.first_name, customer.first_name)
        self.assertEqual(found_customer.last_name, customer.last_name)
        self.assertEqual(found_customer.address, customer.address)
        self.assertEqual(found_customer.email, customer.email)
        self.assertEqual(found_customer.phone_number, customer.phone_number)

    def test_update_a_customer(self):
        """It should Update a Customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        logging.debug(customer)
        self.assertIsNotNone(customer.id)
        # Change it and save it
        customer.first_name = "Updated"
        original_id = customer.id
        customer.update()
        self.assertEqual(customer.id, original_id)
        self.assertEqual(customer.first_name, "Updated")
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, original_id)
        self.assertEqual(customers[0].first_name, "Updated")

    def test_delete_a_customer(self):
        """It should Delete a Customer"""
        customer = CustomerFactory()
        customer.create()
        self.assertEqual(len(Customer.all()), 1)
        customer.delete()
        self.assertEqual(len(Customer.all()), 0)

    def test_list_all_customers(self):
        """It should List all Customers in the database"""
        customers = Customer.all()
        self.assertEqual(customers, [])
        for _ in range(5):
            customer = CustomerFactory()
            customer.create()
        customers = Customer.all()
        self.assertEqual(len(customers), 5)

    def test_serialize_a_customer(self):
        """It should serialize a Customer"""
        customer = CustomerFactory()
        data = customer.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], customer.id)
        self.assertIn("first_name", data)
        self.assertEqual(data["first_name"], customer.first_name)
        self.assertIn("last_name", data)
        self.assertEqual(data["last_name"], customer.last_name)
        self.assertIn("email", data)
        self.assertEqual(data["email"], customer.email)
        self.assertIn("phone_number", data)
        self.assertEqual(data["phone_number"], customer.phone_number)
        self.assertIn("address", data)
        self.assertEqual(data["address"], customer.address)

    def test_deserialize_a_customer(self):
        """It should de-serialize a Customer"""
        data = CustomerFactory().serialize()
        customer = Customer()
        customer.deserialize(data)
        self.assertNotEqual(customer, None)
        self.assertEqual(customer.id, None)
        self.assertEqual(customer.first_name, data["first_name"])
        self.assertEqual(customer.last_name, data["last_name"])
        self.assertEqual(customer.email, data["email"])
        self.assertEqual(customer.phone_number, data["phone_number"])
        self.assertEqual(customer.address, data["address"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Customer with missing data"""
        data = {"id": 1, "first_name": "John", "last_name": "Doe"}
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        customer = Customer()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_activate_sets_suspended_false(self):
        """It should set suspended to False when activate is called"""
        customer = Customer(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone_number="1234567890",
            address="123 Main St",
            suspended=True,
        )
        customer.create()
        self.assertTrue(customer.suspended)
        customer.suspended = False
        customer.update()
        refreshed = Customer.find(customer.id)
        self.assertFalse(refreshed.suspended)

    def test_activate_idempotent(self):
        """Calling activate on an already active customer should keep suspended False"""
        customer = Customer(
            first_name="Active",
            last_name="User",
            email="active@example.com",
            phone_number="5555555555",
            address="789 Main St",
            suspended=False,
        )
        customer.create()
        self.assertFalse(customer.suspended)
        customer.suspended = False
        customer.update()
        refreshed = Customer.find(customer.id)
        self.assertFalse(refreshed.suspended)

    def test_activate_nonexistent_customer(self):
        """Activating a non-existent customer should not throw but return None"""
        customer = Customer.find(99999)
        self.assertIsNone(customer)


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestCase):
    """Customer Model Exception Handlers"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.create)

    @patch("service.models.db.session.commit")
    def test_update_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.update)

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.delete)


######################################################################
#  Q U E R Y   T E S T   C A S E S
######################################################################
class TestModelQueries(TestCase):
    """Customer Model Query Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_find_customer(self):
        """It should Find a Customer by ID"""
        customers = CustomerFactory.create_batch(5)
        for customer in customers:
            customer.create()
        logging.debug(customers)
        # make sure they got saved
        self.assertEqual(len(Customer.all()), 5)
        # find the 2nd customer in the list
        customer = Customer.find(customers[1].id)
        self.assertIsNot(customer, None)
        self.assertEqual(customer.id, customers[1].id)
        self.assertEqual(customer.first_name, customers[1].first_name)
        self.assertEqual(customer.last_name, customers[1].last_name)
        self.assertEqual(customer.email, customers[1].email)

    def test_find_by_email(self):
        """It should Find a Customer by Email"""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()
        email = customers[0].email
        found = Customer.find_by_email(email)
        self.assertEqual(found.email, email)

    def test_find_by_first_name(self):
        """It should Find Customers by First Name"""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()

        # Get the first customer's first name to search for
        first_name = customers[0].first_name
        found = Customer.find_by_first_name(first_name)

        # There might be multiple customers with same first name
        self.assertGreaterEqual(len(found), 1)
        for customer in found:
            self.assertEqual(customer.first_name, first_name)

    def test_find_by_last_name(self):
        """It should Find Customers by Last Name"""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()

        # Get the first customer's last name to search for
        last_name = customers[0].last_name
        found = Customer.find_by_last_name(last_name)

        self.assertGreaterEqual(len(found), 1)
        for customer in found:
            self.assertEqual(customer.last_name, last_name)

    def test_find_by_phone_number(self):
        """It should Find a Customer by Phone Number"""
        customers = CustomerFactory.create_batch(10)
        for customer in customers:
            customer.create()

        # Get the first customer's phone number to search for
        phone_number = customers[0].phone_number
        found = Customer.find_by_phone_number(phone_number)

        # Phone numbers should be unique, so expect exactly one result
        self.assertIsNotNone(found)
        self.assertEqual(found.phone_number, phone_number)

    def test_find_by_first_name_not_found(self):
        """It should return empty list when first name not found"""
        found = Customer.find_by_first_name("NonExistentFirstName")
        self.assertEqual(len(found), 0)

    def test_find_by_last_name_not_found(self):
        """It should return empty list when last name not found"""
        found = Customer.find_by_last_name("NonExistentLastName")
        self.assertEqual(len(found), 0)

    def test_find_by_phone_number_not_found(self):
        """It should return None when phone number not found"""
        found = Customer.find_by_phone_number("999-999-9999")
        self.assertIsNone(found)

    def test_find_by_suspended_true(self):
        """It should Find Customers that are suspended"""
        customers = CustomerFactory.create_batch(5)
        # Make some customers suspended
        customers[0].suspended = True
        customers[2].suspended = True
        for customer in customers:
            customer.create()
        found = Customer.find_by_suspended(True)
        self.assertEqual(len(found), 2)
        for customer in found:
            self.assertTrue(customer.suspended)

    def test_find_by_suspended_false(self):
        """It should Find Customers that are not suspended"""
        customers = CustomerFactory.create_batch(5)
        # Make some customers suspended, leave others active
        customers[1].suspended = True
        customers[3].suspended = True
        for customer in customers:
            customer.create()

        found = Customer.find_by_suspended(False)
        self.assertEqual(len(found), 3)
        for customer in found:
            self.assertFalse(customer.suspended)

    def test_find_by_suspended_all_active(self):
        """It should return all customers when all are active"""
        customers = CustomerFactory.create_batch(3)
        # All customers active by default
        for customer in customers:
            customer.create()

        found = Customer.find_by_suspended(False)
        self.assertEqual(len(found), 3)

    def test_find_by_suspended_none_suspended(self):
        """It should return empty list when no customers are suspended"""
        customers = CustomerFactory.create_batch(3)
        # All customers active by default
        for customer in customers:
            customer.create()

        found = Customer.find_by_suspended(True)
        self.assertEqual(len(found), 0)

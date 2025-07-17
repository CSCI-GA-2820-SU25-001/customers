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
Customer Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customer
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Customer, DataValidationError
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")

######################################################################
# CREATE A NEW CUSTOMER
######################################################################
@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Create a Customer
    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to Create a Customer...")
    check_content_type("application/json")

    customer = Customer()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer.deserialize(data)

    # Save the new Customer to the database
    customer.create()
    app.logger.info("Customer with new id [%s] saved!", customer.id)

    # Return the location of the new Customer
    location_url = url_for("get_customers", customer_id=customer.id, _external=True)
    return (
        jsonify(customer.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# GET CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customers(customer_id):
    """
    Retrieve a single Customer

    This endpoint will return a customer based on it's id
    """
    app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)

    # Attempt to find the customer and abort if not found
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    app.logger.info(
        "Returning customer: %s %s", customer.first_name, customer.last_name
    )
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customers(customer_id):
    """
    Update a Customer
    This endpoint will update a Customer based the body that is posted
    """
    app.logger.info("Request to Update a customer with id [%s]", customer_id)
    check_content_type("application/json")

    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer.deserialize(data)
    customer.update()

    app.logger.info("Customer with ID: %d updated.", customer.id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
    """
    Delete a Customer

    This endpoint will delete a Customer based the id specified in the path
    """
    app.logger.info("Request to Delete a customer with id [%s]", customer_id)

    # Delete the Customer if it exists
    customer = Customer.find(customer_id)
    if customer:
        app.logger.info("Customer with ID: %d found.", customer.id)
        customer.delete()

    app.logger.info("Customer with ID: %d delete complete.", customer_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL CUSTOMERS
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the Customers"""

    app.logger.info("Request for customer list")
    # Parse any arguments from the query string
    email = request.args.get("email")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    phone_number = request.args.get("phone_number")
    suspended = request.args.get("suspended")  # ADD THIS LINE

    # Start with base query
    query = Customer.query

    # Apply filters based on query parameters
    if email:
        app.logger.info("Find by email: %s", email)
        query = query.filter(Customer.email == email)

    if first_name:
        app.logger.info("Find by first_name (partial, case-insensitive): %s", first_name)
        query = query.filter(Customer.first_name.ilike(f"%{first_name}%"))

    if last_name:
        app.logger.info("Find by last_name (partial, case-insensitive): %s", last_name)
        query = query.filter(Customer.last_name.ilike(f"%{last_name}%"))

    if phone_number:
        app.logger.info("Find by phone_number: %s", phone_number)
        query = query.filter(Customer.phone_number == phone_number)

    if suspended is not None:
        # Convert string to boolean (handles 'true', 'false', '1', '0', etc.)
        suspended_bool = suspended.lower() in ('true', '1', 'yes')
        app.logger.info("Find by suspended: %s", suspended_bool)
        query = query.filter(Customer.suspended == suspended_bool)

    # Execute the query to get filtered results
    customers = query.all()

    # Serialize the results
    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# SUSPEND A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>/suspend", methods=["PUT"])
def suspend_customer(customer_id):
    """
    Suspend a Customer
    This endpoint will suspend an existing customer's account
    """
    app.logger.info("Request to suspend customer with id [%s]", customer_id)

    # Find the customer
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    # Add suspended field to customer data
    customer.suspended = True
    customer.update()

    app.logger.info("Customer with ID [%s] has been suspended", customer_id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# ACTIVATE A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>/activate", methods=["PUT"])
def activate_customer(customer_id):
    """
    Activate a Customer
    This endpoint will activate (unsuspend) an existing customer's account
    """
    app.logger.info("Request to activate customer with id [%s]", customer_id)

    # Find the customer
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    # Set suspended to False to activate
    customer.suspended = False
    customer.update()

    app.logger.info("Customer with ID [%s] has been activated", customer_id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Error Handlers -- added in add-create-customer
######################################################################
@app.errorhandler(DataValidationError)
def handle_data_validation_error(error):
    """Handles bad input data and returns a 400"""
    app.logger.error("DataValidationError: %s", str(error))
    return jsonify({"error": str(error)}), status.HTTP_400_BAD_REQUEST

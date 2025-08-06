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
from flask_restx import Api, Resource, fields
from service.models import Customer
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
    """Base URL for our service (serves the UI)"""
    return app.send_static_file("index.html")


######################################################################
# GET API METADATA (Endpoint for API documentation/metadata)
######################################################################
@app.route("/api")
def api_metadata():
    """Returns API documentation/metadata"""
    return (
        jsonify(
            name="Customer REST API Service",
            version="1.0.0",
            paths={
                "create": url_for("customer_collection", _external=True),
                "list_all": url_for("customer_collection", _external=True),
                "read_one": url_for("customer_resource", customer_id=0, _external=True),
                "update": url_for("customer_resource", customer_id=0, _external=True),
                "delete": url_for("customer_resource", customer_id=0, _external=True),
                "suspend": url_for(
                    "customer_suspend_resource", customer_id=0, _external=True
                ),
                "activate": url_for(
                    "customer_activate_resource", customer_id=0, _external=True
                ),
                "find_by_email": url_for(
                    "customer_collection", email="test@example.com", _external=True
                ),
            },
        ),
        status.HTTP_200_OK,
    )


######################################################################
# Update API initialization to use /api prefix and /apidocs/ for docs
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Customer REST API Service",
    description="This is a sample server for managing customers.",
    default="customers",
    default_label="Customer operations",
    doc="/apidocs/",
    prefix="/api",
)

######################################################################
# Define the customer model for documentation and validation
######################################################################
customer_model = api.model(
    "Customer",
    {
        "first_name": fields.String(
            required=True, description="First name of the customer"
        ),
        "last_name": fields.String(
            required=True, description="Last name of the customer"
        ),
        "email": fields.String(
            required=True, description="Email address of the customer"
        ),
        "phone_number": fields.String(
            required=False, description="Phone number of the customer"
        ),
        "address": fields.String(required=False, description="Address of the customer"),
        "suspended": fields.Boolean(
            required=False, description="Is the customer suspended?"
        ),
        # Add other fields as needed
    },
)

customer_response_model = api.inherit(
    "CustomerResponse",
    customer_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique identifier of a customer"
        ),
    },
)


######################################################################
# GET CUSTOMER
######################################################################
@api.route("/customers/<int:customer_id>")
@api.param("customer_id", "The Customer identifier")
class CustomerResource(Resource):
    """
    Resource for handling single Customer operations (GET, PUT, DELETE).
    Provides endpoints to retrieve, update, or delete a specific customer by ID.
    """

    @api.doc("get_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_response_model)
    def get(self, customer_id):
        """
        Retrieve a single Customer
        This endpoint will return a customer based on its id
        """
        app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        app.logger.info(
            "Returning customer: %s %s", customer.first_name, customer.last_name
        )
        return customer.serialize(), status.HTTP_200_OK

    @api.doc("update_customers")
    @api.expect(customer_model)
    @api.response(404, "Customer not found")
    @api.response(400, "The posted Customer data was not valid")
    @api.marshal_with(customer_response_model)
    def put(self, customer_id):
        """
        Update a Customer
        This endpoint will update a Customer based on the body that is posted
        """
        app.logger.info("Request to Update a customer with id [%s]", customer_id)
        check_content_type("application/json")
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        data = api.payload
        app.logger.info("Processing: %s", data)
        customer.deserialize(data)
        customer.update()
        app.logger.info("Customer with ID: %d updated.", customer.id)
        return customer.serialize(), status.HTTP_200_OK

    @api.doc("delete_customers")
    @api.response(204, "Customer deleted")
    def delete(self, customer_id):
        """
        Delete a Customer
        This endpoint will delete a Customer based on the id specified in the path
        """
        app.logger.info("Request to Delete a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if customer:
            app.logger.info("Customer with ID: %d found.", customer.id)
            customer.delete()
        app.logger.info("Customer with ID: %d delete complete.", customer_id)
        return "", status.HTTP_204_NO_CONTENT


@api.route("/customers")
class CustomerCollection(Resource):
    """
    Resource for handling Customer collection operations (POST, GET).
    Provides endpoints to create a new customer or list/query all customers.
    """

    @api.doc("create_customers")
    @api.expect(customer_model)
    @api.marshal_with(customer_response_model, code=201)
    def post(self):
        """
        Create a Customer
        This endpoint will create a Customer based on the data in the body that is posted
        """
        app.logger.info("Request to Create a Customer...")
        check_content_type("application/json")

        customer = Customer()
        # Get the data from the request and deserialize it
        data = api.payload
        app.logger.info("Processing: %s", data)
        customer.deserialize(data)

        # Save the new Customer to the database
        customer.create()
        app.logger.info("Customer with new id [%s] saved!", customer.id)

        # Return the location of the new Customer
        location_url = url_for(
            "customer_resource", customer_id=customer.id, _external=True
        )
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    @api.doc("list_customers")
    @api.param("email", "Filter by email")
    @api.param("first_name", "Filter by first name")
    @api.param("last_name", "Filter by last name")
    @api.param("phone_number", "Filter by phone number")
    @api.param("suspended", "Filter by suspended status (true/false)")
    @api.marshal_list_with(customer_response_model)
    def get(self):
        """Returns all of the Customers"""
        app.logger.info("Request for customer list")
        email = request.args.get("email")
        first_name = request.args.get("first_name")
        last_name = request.args.get("last_name")
        phone_number = request.args.get("phone_number")
        suspended = request.args.get("suspended")
        query = Customer.query
        if email:
            app.logger.info("Find by email: %s", email)
            query = query.filter(Customer.email == email)
        if first_name:
            app.logger.info(
                "Find by first_name (partial, case-insensitive): %s", first_name
            )
            query = query.filter(Customer.first_name == first_name)
        if last_name:
            app.logger.info(
                "Find by last_name (partial, case-insensitive): %s", last_name
            )
            query = query.filter(Customer.last_name.ilike(f"%{last_name}%"))
        if phone_number:
            app.logger.info("Find by phone_number: %s", phone_number)
            query = query.filter(Customer.phone_number == phone_number)
        if suspended is not None:
            suspended_bool = suspended.lower() in ("true", "1", "yes")
            app.logger.info("Find by suspended: %s", suspended_bool)
            query = query.filter(Customer.suspended == suspended_bool)
        customers = query.all()
        results = [customer.serialize() for customer in customers]
        app.logger.info("Returning %d customers", len(results))
        return results, status.HTTP_200_OK


@api.route("/customers/<int:customer_id>/suspend")
@api.param("customer_id", "The Customer identifier")
class CustomerSuspendResource(Resource):
    """
    Resource for suspending a Customer account.
    Provides an endpoint to suspend a specific customer by ID.
    """

    @api.doc("suspend_customer")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_response_model)
    def put(self, customer_id):
        """
        Suspend a Customer
        This endpoint will suspend an existing customer's account
        """
        app.logger.info("Request to suspend customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.suspended = True
        customer.update()
        app.logger.info("Customer with ID [%s] has been suspended", customer_id)
        return customer.serialize(), status.HTTP_200_OK


@api.route("/customers/<int:customer_id>/activate")
@api.param("customer_id", "The Customer identifier")
class CustomerActivateResource(Resource):
    """
    Resource for activating (unsuspending) a Customer account.
    Provides an endpoint to activate a specific customer by ID.
    """

    @api.doc("activate_customer")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_response_model)
    def put(self, customer_id):
        """
        Activate a Customer
        This endpoint will activate (unsuspend) an existing customer's account
        """
        app.logger.info("Request to activate customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.suspended = False
        customer.update()
        app.logger.info("Customer with ID [%s] has been activated", customer_id)
        return customer.serialize(), status.HTTP_200_OK


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

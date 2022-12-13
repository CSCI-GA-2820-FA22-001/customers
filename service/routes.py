# pylint: disable=cyclic-import
"""
My Service

Describe what your service does here
"""

from flask import jsonify, request
from flask_restx import Resource, fields, reqparse, inputs
from service.models import Customer
from .common import status

# Import Flask application
from . import app, api


############################################################
# Health Endpoint
############################################################


@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


def check_content_type(content_type):
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


addresses = {
    "name": fields.String(
        zrequired=True, description="The name of the address (ex.: Home)"
    ),
    "street": fields.String(
        required=True, description="The name of the street and number"
    ),
    "city": fields.String(
        required=True, description="The name of the city"
    ),
    "state": fields.String(
        required=True, description="The name of the state"
    ),
    "postalcode": fields.String(
        required=True, description="The postal code is"
    ),
}

create_model = api.model(
    "Customer",
    {
        "first_name": fields.String(
            required=True, description="The first name of the Customer"
        ),
        "last_name": fields.String(
            required=True, description="The last name of the Customer"
        ),
        "active": fields.Boolean(required=True, description="Is the Customer active?"),
        "addresses": fields.List(fields.Nested(api.model("addresses", addresses))),
    },
)

customer_model = api.inherit(
    "CustomerModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
customer_args = reqparse.RequestParser()
customer_args.add_argument(
    "first_name",
    type=str,
    location="args",
    required=False,
    help="List Customers by first name",
)
customer_args.add_argument(
    "last_name",
    type=str,
    location="args",
    required=False,
    help="List Customers by last name",
)
customer_args.add_argument(
    "active",
    type=inputs.boolean,
    location="args",
    required=False,
    help="List Customers by active",
)

######################################################################
#  PATH: /customers/{id}
######################################################################


@api.route("/customers/<int:customer_id>", strict_slashes=False)
@api.param("customer_id", "The Customer identifier")
class CustomerResource(Resource):
    """
    CustomerResource class
    Allows the manipulation of a single customer
    GET /customer_id - Returns a Customer with the id
    PUT /customer_id - Update a Customer with the id
    DELETE /customer_id -  Deletes a Customer with the id
    """

    ######################################################################
    # RETRIEVE A CUSTOMER
    ######################################################################

    @api.doc("get_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        """
        Retrieve a single customer
        This endpoint will return a customer based on id
        """
        app.logger.info("Request for customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )

        app.logger.info("Returning customer: %s", customer.f_name)
        return customer.serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE AN EXISTING CUSTOMER
    ######################################################################
    @api.doc("update_customers")
    @api.response(404, "Customer not found")
    @api.response(400, "The posted customer data was not valid")
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Update a customer
        This endpoint will update a customer based on the body that is posted
        """
        app.logger.info("Request to update customer with id: %s", customer_id)
        check_content_type("application/json")

        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        customer.deserialize(data)
        customer.id = customer_id
        customer.update()

        app.logger.info("Customer with ID [%s] updated.", customer.id)
        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )
        return customer.serialize(), status.HTTP_200_OK, {"Location": location_url}

    ######################################################################
    # DELETE A CUSTOMER
    ######################################################################
    @api.doc("delete_customers")
    @api.response(204, "Customer deleted")
    # @app.route("/customers/<int:customer_id>", methods=["DELETE"])
    def delete(self, customer_id):
        """
        Delete a customer
        This endpoint will delete a customer based the id specified in the path
        """
        app.logger.info("Request to delete customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.delete()
        app.logger.info("customer with ID [%s] delete complete.", customer_id)
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /customers
######################################################################
@api.route("/customers", strict_slashes=False)
class CustomerCollection(Resource):
    """
    CustomerCollection class
    Allows the manipulation of all of your customers
    GET /customers - Returns a list all of the customers
    POST /customers - creates a new customer record in the database
    """

    ######################################################################
    # LIST ALL CUSTOMERS
    ######################################################################
    @api.doc("list_customers")
    @api.expect(customer_args, validate=True)
    @api.marshal_list_with(customer_model)
    def get(self):
        """
        List all customers
        This endpoint will list all customers currently listed in the database
        Returns:
            json: an array of customer data
        """
        app.logger.info("Request to list all customers")
        customers = []

        active = request.args.get("active")

        if active:
            app.logger.info("Filtering by active: %s", active)
            is_active = active.lower() in ["yes", "y", "true", "t", "1"]
            customers = Customer.find_by_activity(is_active)
        else:
            customers = Customer.all()

        results = [customer.serialize() for customer in customers]
        app.logger.info("Returning %d customers", len(results))
        return results, status.HTTP_200_OK

    ######################################################################
    # ADD A NEW CUSTOMER
    ######################################################################
    @api.doc("create_customers")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(customer_model, code=201)
    def post(self):
        """
        Creates a customer
        This endpoint will create a customer based the data in the body that is posted
        """
        app.logger.info("Request to create a customer")
        check_content_type("application/json")
        customer = Customer()
        app.logger.info("Payload = %s", api.payload)
        customer.deserialize(api.payload)
        app.logger.info("Customer : %s", customer.serialize())
        customer.create()

        app.logger.info("Customer : %s", customer.serialize())
        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )

        app.logger.info("Customer : ", customer.serialize())
        app.logger.info("Customer with ID [%s] created.", customer.id)
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /customers/<customer_id>/activate
######################################################################
@api.route("/customers/<int:customer_id>/activate", strict_slashes=False)
@api.param("customer_id", "The Customer identifier")
class ActivateResource(Resource):
    """
    ActivateResource class
    Allows the activation of a single customer
    PUT /customer_id/activate - Make a customer active
    """

    @api.doc("activate_customers")
    @api.response(200, "Successfully activated")
    @api.response(404, "Customer not found")
    @api.response(409, "The Customer is not available for activation")
    def put(self, customer_id):
        """
        Activate a customer
        This endpoint will activate a customer based the body that is posted
        """

        app.logger.info("Request to activate customer with id: %s", customer_id)

        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.activate()
        app.logger.info(
            "Customer with ID [%s]'s active status is set to [%s].",
            customer.id,
            customer.active,
        )
        return customer.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /customers/<customer_id>/deactivate
######################################################################
@api.route("/customers/<int:customer_id>/deactivate", strict_slashes=False)
@api.param("customer_id", "The Customer identifier")
class DeactivateResource(Resource):
    """
    DeactivateResource class
    Allows the deactivation of a single customer
    PUT /customer_id/activate - Make a customer non-active
    """

    @api.doc("deactivate_customers")
    @api.response(200, "Successfully deactivated")
    @api.response(404, "Customer not found")
    @api.response(409, "The Customer is not available for deactivation")
    def put(self, customer_id):
        """
        Deactivate a customer
        This endpoint will deactivate a customer based on the body that is posted
        """
        app.logger.info("Request to deactivate customer with id: %s", customer_id)
        # check_content_type("application/json")

        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.deactivate()
        app.logger.info(
            "Customer with ID [%s]'s active status is set to [%s].",
            customer.id,
            customer.active,
        )
        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )
        return customer.serialize(), status.HTTP_200_OK, {"Location": location_url}

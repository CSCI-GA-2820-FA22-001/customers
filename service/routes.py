# pylint: disable=cyclic-import
"""
My Service

Describe what your service does here
"""

from functools import wraps
from flask import abort, jsonify, request, url_for, make_response, render_template
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Customer,  DataValidationError
from service.common import error_handlers, status    # HTTP Status Codes
from . import app, api
 # HTTP Status Codes
from .common import status 



############################################################
# Health Endpoint
############################################################


@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK

######################################################################
# Configure the Root route before OpenAPI
######################################################################

# Create website page
@app.route('/')
def index():
    """ Index page """
    return app.send_static_file('index.html')

# Define the model so that the docs reflect what can be sent
create_model = api.model('Customer', {
    'f_name': fields.String(required=True,
                          description='The first name of the Customer'),
    'l_name': fields.String(required=True,
                              description='The last name of the Customer'),
    'active': fields.Boolean(required=True,
                                description='Is the Customer active ?'),
})

customer_model = api.inherit(
    'CustomerModel', 
    create_model,
    {
        '_id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)

# query string arguments
customer_args = reqparse.RequestParser()
customer_args.add_argument('f_name', type=str, location='args', required=False, help='List Customers by first name')
customer_args.add_argument('l_name', type=str, location='args', required=False, help='List Customers by last name')
customer_args.add_argument('active', type=inputs.boolean, location='args', required=False, help='List Customers by active')



######################################################################
#  PATH: /customers/{id}
######################################################################
@api.route('/customers/<customer_id>')
@api.param('customer_id', 'The Customer identifier')
class CustomerResource(Resource):
   

    ######################################################################
    # RETRIEVE A CUSTOMER
    ######################################################################

    @api.doc('get_customers')
    @api.response(404, 'Customer not found')
    @api.marshal_with(customer_model)
    #@app.route("/customers/<int:customer_id>", methods=["GET"])
    def get(self, customer_id):
        """
        Retrieve a single Customer

        This endpoint will return a Customer based on id
        """
        app.logger.info("Request for customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.")

        app.logger.info("Returning customer: %s", customer.f_name)
        return jsonify(customer.serialize()), status.HTTP_200_OK


    ######################################################################
    # UPDATE AN EXISTING Customer
    ######################################################################
    @api.doc('update_customers')
    @api.response(404, 'Customer not found')
    @api.response(400, 'The posted Customer data was not valid')
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    #@app.route("/customers/<int:customer_id>", methods=["PUT"])
    def put(self, customer_id):
        """
        Update a Customer

        This endpoint will update a Customer based the body that is posted
        """
        app.logger.info("Request to update customer with id: %s", customer_id)
        #check_content_type("application/json")

        customer = Customer.find(customer_id)
        if not customer:
            abort(status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.")
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        customer.deserialize(data)
        customer.id = customer_id
        customer.update()

        app.logger.info("Customer with ID [%s] updated.", customer.id)
        return customer.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A customer
    ######################################################################
    @api.doc('delete_customers')
    @api.response(204,'Customer deleted')
    #@app.route("/customers/<int:customer_id>", methods=["DELETE"])
    def delete(self, customer_id):
        """
        Delete a customer

        This endpoint will delete a customer based the id specified in the path
        """
        app.logger.info("Request to delete customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if customer:
            customer.delete()

        app.logger.info("customer with ID [%s] delete complete.", customer_id)
        return "", status.HTTP_204_NO_CONTENT


   
######################################################################
#  PATH: /customers
######################################################################
@api.route('/customers', strict_slashes=False)
class CustomerCollection(Resource):
    ######################################################################
    # LIST ALL CUSTOMERS (Needs to be adjusted for RestX)
    ######################################################################
    @api.doc('list_customers')
    @api.expect(customer_args, validate=True)
    @api.marshal_list_with(customer_model)
    #@app.route("/customers", methods=["GET"])
   
    def get(self):
        """
        List all Customers
        This endpoint will list all Customers currently listed in the database
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
        return jsonify(results), status.HTTP_200_OK

    ######################################################################
    # ADD A NEW CUSTOMER
    ######################################################################
    #@app.route("/customers", methods=["POST"])
    @api.doc('create_customers')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(customer_model, code=201)
    def post(self):
        """
        Creates a Customer
        This endpoint will create a Customer based the data in the body that is posted
        """
        app.logger.info("Request to create a customer")
        check_content_type("application/json")
        customer = Customer()
        app.logger.debug('Payload = %s', api.payload)
        customer.deserialize(api.payload)
        customer.create()
        location_url = url_for(
            "get_customers", customer_id=customer.id, _external=True)

        app.logger.info("Customer with ID [%s] created.", customer.id)
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


############################################################
# Active Endpoint
############################################################


@app.route("/customers/<int:customer_id>/activate", methods=["PUT"])
def activate_customer(customer_id):
    """
    Activate a Customer

    This endpoint will activate a Customer based the body that is posted
    """

    app.logger.info("Request to activate customer with id: %s", customer_id)

    customer = Customer.find(customer_id)
    if not customer:
        abort(status.HTTP_404_NOT_FOUND,
              f"Customer with id '{customer_id}' was not found.")
    customer.activate()
    app.logger.info("Customer with ID [%s]'s active status is set to [%s].",
                    customer.id, customer.active)
    return jsonify(customer.serialize()), status.HTTP_200_OK


# ############################################################
# # Deactive Endpoint
# ############################################################


@app.route("/customers/<int:customer_id>/deactivate", methods=["PUT"])
def deactivate_customer(customer_id):
    """
    Deactivate a Customer
    This endpoint will deactivate a Customer based the body that is posted
    """
    app.logger.info("Request to deactivate customer with id: %s", customer_id)
    # check_content_type("application/json")

    customer = Customer.find(customer_id)
    if not customer:
        abort(status.HTTP_404_NOT_FOUND,
              f"Customer with id '{customer_id}' was not found.")
    customer.deactivate()
    app.logger.info("Customer with ID [%s]'s active status is set to [%s].",
                    customer.id, customer.active)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
#  PATH: /customers/<customer_id>/activate
######################################################################
@api.route('/customers/<customer_id>/activate')
@api.param('customer_id', 'The Customer activator')
class ActivateResource(Resource):
    """ Activate actions on a Pet """
    @api.doc('activate_customers')
    @api.response(404, 'Customer not found')
    @api.response(409, 'The Customer is not available for activation')
    def put(self, customer_id):
        """
        Activate a Customer

        This endpoint will activate a Customer based the body that is posted
        """

        app.logger.info("Request to activate customer with id: %s", customer_id)

        customer = Customer.find(customer_id)
        if not customer:
            abort(status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.")
        customer.activate()
        app.logger.info("Customer with ID [%s]'s active status is set to [%s].",
                        customer.id, customer.active)
        return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
#  PATH: /customers/<customer_id>/deactivate
######################################################################
@api.route('/customers/<customer_id>/deactivate')
@api.param('customer_id', 'The Customer deactivator')
class DeactivateResource(Resource):
    """ Deactivate actions on a Pet """
    @api.doc('deactivate_customers')
    @api.response(404, 'Customer not found')
    @api.response(409, 'The Customer is not available for deactivation')
    def put(self, customer_id):
        """
        Deactivate a Customer
        This endpoint will deactivate a Customer based the body that is posted
        """
        app.logger.info("Request to deactivate customer with id: %s", customer_id)
        # check_content_type("application/json")

        customer = Customer.find(customer_id)
        if not customer:
            abort(status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.")
        customer.deactivate()
        app.logger.info("Customer with ID [%s]'s active status is set to [%s].",
                        customer.id, customer.active)
        return jsonify(customer.serialize()), status.HTTP_200_OK

######################################################################
# GET INDEX
######################################################################


#@app.route("/")
#def index():
#    """Base URL for our service"""
#    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


# def init_db():
#     """ Initializes the SQLAlchemy app """
#     global app
#     Customer.init_db(app)


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {content_type}", )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s",
                     request.headers["Content-Type"])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
          f"Content-Type must be {content_type}", )
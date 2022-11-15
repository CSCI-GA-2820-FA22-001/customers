# pylint: disable=cyclic-import
"""
My Service

Describe what your service does here
"""

from flask import abort, jsonify, request, url_for

from service.models import Customer

# Import Flask application
from . import app
from .common import status  # HTTP Status Codes

############################################################
# Health Endpoint
############################################################


@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


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
    app.logger.info("Customer with ID [%s]'s active status is set to [%s].", customer.id,customer.active)
    return jsonify(customer.serialize()), status.HTTP_200_OK

# ############################################################
# # Deactive Endpoint
# ############################################################


@app.route("/customers/<int:customer_id>/deactivate",methods=["PUT"])
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
    app.logger.info("Customer with ID [%s]'s active status is set to [%s].", customer.id,customer.active)
    return jsonify(customer.serialize()), status.HTTP_200_OK

    

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(name="Customer Demo REST API Service", version="1.0",
                # paths=url_for("list_customers", _external=True),
                ), status.HTTP_200_OK,)


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


######################################################################
# ADD A NEW CUSTOMER
######################################################################
@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Creates a Customer
    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to create a customer")
    check_content_type("application/json")
    customer = Customer()
    customer.deserialize(request.get_json())
    customer.create()
    message = customer.serialize()
    location_url = url_for(
        "get_customers", customer_id=customer.id, _external=True)

    app.logger.info("Customer with ID [%s] created.", customer.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# RETRIEVE A CUSTOMER
######################################################################


@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customers(customer_id):
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
# LIST ALL CUSTOMERS
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
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
# DELETE A customer
######################################################################
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
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
# UPDATE AN EXISTING Customer
######################################################################
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customers(customer_id):
    """
    Update a Customer

    This endpoint will update a Customer based the body that is posted
    """
    app.logger.info("Request to update customer with id: %s", customer_id)
    check_content_type("application/json")

    customer = Customer.find(customer_id)
    if not customer:
        abort(status.HTTP_404_NOT_FOUND,
              f"Customer with id '{customer_id}' was not found.")

    customer.deserialize(request.get_json())
    customer.id = customer_id
    customer.update()

    app.logger.info("Customer with ID [%s] updated.", customer.id)
    return jsonify(customer.serialize()), status.HTTP_200_OK

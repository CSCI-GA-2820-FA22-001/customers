"""
Models for Customer
All of the models are stored in this module
"""
import logging

from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Customer.init_db(app)


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    def create(self):
        """
        Creates a Customer to the database
        """
        logger.info("Creating %s %s", self.f_name, self.l_name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Customer to the database
        """
        logger.info("Updating %s", self.__str__)
        db.session.commit()

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s", self.__str__)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  A D D R E S S   M O D E L
######################################################################
class Address(db.Model, PersistentBase):
    """
    Class that represents an Address
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(64))  #e.g. primary, summer home, etc
    street = db.Column(db.String(64))
    city = db.Column(db.String(64))
    state = db.Column(db.String(2))
    postalcode = db.Column(db.String(16))

    def __repr__(self):
        return f"<Address {self.name} id=[{self.id}] customer[{self.customer_id}]>"

    def __str__(self):
        return f"{self.name}: {self.street}, {self.city}, {self.state} {self.postalcode}"

    def serialize(self):
        """Serializes a Address into a dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "name": self.name,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postalcode": self.postalcode
        }

    def deserialize(self, data):
        """
        Deserializes a Address from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            # self.customer_id = data["customer_id"]
            self.name = data["name"]
            self.street = data["street"]
            self.city = data["city"]
            self.state = data["state"]
            self.postalcode = data["postalcode"]
        except KeyError as error:
            raise DataValidationError("Invalid Address: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Address: body of request contained "
                "bad or no data " + error.args[0]
            ) from error
        return self


######################################################################
#  C U S T O M E R   M O D E L
######################################################################
class Customer(db.Model, PersistentBase):
    """
    Class that represents a Customer
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(64))
    l_name = db.Column(db.String(64))
    active = db.Column(db.Boolean, default=True)
    addresses = db.relationship("Address", backref="customer", passive_deletes=True)

    def __repr__(self):
        return f"<Customer {self.f_name} {self.l_name} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        customer = {
            "id": self.id,
            "f_name": self.f_name,
            "l_name": self.l_name,
            "active": self.active,
            "addresses": [],
        }
        for address in self.addresses:
            customer["addresses"].append(address.serialize())
        return customer

    def deserialize(self, data):
        """
        Deserializes a Account from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.f_name = data["f_name"]
            self.l_name = data["l_name"]
            self.active = data["active"]
            # handle inner list of addresses
            address_list = data.get("addresses")
            for json_address in address_list:
                address = Address()
                address.deserialize(json_address)
                self.addresses.append(address)
        except KeyError as error:
            raise DataValidationError("Invalid Customer: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

    @classmethod
    def find_by_name(cls, f_name, l_name):
        """Returns all Customers with the given f_name and l_name
        Args:
            f_name (string): the f_name of the Customer you want to match
            l_name (string): the l_name of the Customer you want to match
        """
        logger.info("Processing name query for %s %s ...", f_name, l_name)
        return cls.query.filter(cls.f_name == f_name, cls.l_name == l_name)
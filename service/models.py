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
    name = db.Column(db.String(64))
    street = db.Column(db.String(64))
    city = db.Column(db.String(64))
    state = db.Column(db.String(2))
    postalcode = db.Column(db.String(16))

    def __repr__(self):
        return f"<Customer {self.f_name} {self.l_name} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        customer = {
            "id": self.id,
            "first_name": self.f_name,
            "last_name": self.l_name,
            "active": self.active,
            "addresses": [],
        }
        address_object = {
            "name": self.name,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postalcode": self.postalcode
        }
        customer["addresses"].append(address_object)
        return customer

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.f_name = data["first_name"]
            self.l_name = data["last_name"]
            self.active = data["active"]
            # handle inner list of addresses
            address_list = data.get("addresses")
            the_address = address_list[0]
            self.name = the_address["name"]
            self.street = the_address["street"]
            self.city = the_address["city"]
            self.state = the_address["state"]
            self.postalcode = the_address["postalcode"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

    def deactivate(self):
        """
        Sets the active flag to false
        """
        self.active = False

    def activate(self):
        """
        Sets the active flag to true
        """
        self.active = True

    @classmethod
    def find_by_name(cls, f_name, l_name):
        """Returns all Customers with the given first_name and last_name
        Args:
            first_name (string): the first_name of the Customer you want to match
            last_name (string): the last_name of the Customer you want to match
        """
        logger.info("Processing name query for %s %s ...", f_name, l_name)
        return cls.query.filter(cls.f_name == f_name, cls.l_name == l_name)

    @classmethod
    def find_by_activity(cls, active: bool = True) -> list:
        """Returns all Customers by their activity

        :param active: True for customers that are active
        :type active: str

        :return: a collection of Customers that are active
        :rtype: list

        """
        logger.info("Processing activity query for %s ...", active)
        return cls.query.filter(cls.active == active)

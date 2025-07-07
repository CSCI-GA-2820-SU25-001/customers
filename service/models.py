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


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(63))
    last_name = db.Column(db.String(63))
    address = db.Column(db.String(256))
    phone_number = db.Column(db.String(50))
    email = db.Column(db.String(120))

    def __repr__(self):
        return f"<Customer {self.first_name} {self.last_name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Customer to the database
        """
        logger.info("Creating %s %s", self.first_name, self.last_name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Customer to the database
        """
        logger.info("Updating %s %s", self.first_name, self.last_name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s %s", self.first_name, self.last_name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
        }

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number")
            self.address = data.get("address")
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################
    @classmethod
    def all(cls):
        """Returns all of the Customers in the database"""
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_email(cls, email):
        """Returns a Customer with the given email"""
        logger.info("Processing email query for %s ...", email)
        return cls.query.filter(cls.email == email).first()
    
    @classmethod
    def find_by_email_contains(cls, email_part):
        """Returns all Customers whose email contains the given string"""
        logger.info("Processing email contains query for %s ...", email_part)
        return cls.query.filter(cls.email.ilike(f'%{email_part}%')).all()

    @classmethod
    def find_by_domain(cls, domain):
        """Returns all Customers with the given email domain"""
        logger.info("Processing domain query for %s ...", domain)
        return cls.query.filter(cls.email.ilike(f'%@{domain}')).all()
        
    @classmethod
    def validate_email_format(cls, email):
        """Basic email format validation"""
        if not email or '..' in email or ' ' in email:
            return False
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        # Handle single character local/domain parts
        simple_pattern = r'^[a-zA-Z0-9]@[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None or re.match(simple_pattern, email) is not None

    @classmethod
    def validate_domain_format(cls, domain):
        """Basic domain format validation"""
        if not domain or '..' in domain or ' ' in domain or domain.startswith('.') or domain.endswith('.'):
            return False
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        # Handle simple domains like a.co
        simple_pattern = r'^[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        return re.match(pattern, domain) is not None or re.match(simple_pattern, domain) is not None

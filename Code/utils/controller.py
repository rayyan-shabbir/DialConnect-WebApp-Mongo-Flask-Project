from .models import User, SentencesCollection, InsurancesCollection, ActionsCollection, IndividualCollection
from .db import DBManager

# Controller class to handle business logic and interactions between models and the database
class Controller:
    """
    A class to handle business logic and interactions between models and the database.
    """

    def __init__(self):
        """
        Initialize the Controller with instances of DBManager and various models.
        """
         # Initialize the DBManager instance
        self.db_manager = DBManager()
        # Initialize the User model with the DBManager instance
        self.user = User(self.db_manager)
        # Initialize the SentencesCollection model with the 'sentences' collection
        self.sentences_collection = SentencesCollection(self.db_manager.get_collection('sentences'))
         # Initialize the InsurancesCollection model with the 'insurances' collection
        self.insurances_collection = InsurancesCollection(self.db_manager.get_collection('insurances'))
         # Initialize the ActionsCollection model with the 'actions' collection
        self.actions_collection = ActionsCollection(self.db_manager.get_collection('actions'))
         # Initialize the IndividualCollection model with the 'individual' collection
        self.individual_collection = IndividualCollection(self.db_manager.get_collection('individual'))

    # Check if an email is already registered
    def is_email_registered(self, email):
        """
        Check if an email is already registered in the database.

        :param email: The email to check.
        :return: True if the email is registered, False otherwise.
        """
        return self.user.is_email_registered(email)

    # Register a new user
    def register_user(self, name, email, password, organization, designation):
        """
        Register a new user in the database.

        :param name: The name of the user.
        :param email: The email of the user.
        :param password: The password of the user.
        :param organization: The organization the user belongs to.
        :param designation: The designation of the user.
        """
        self.user.register_user(name, email, password, organization, designation)

    # Check if the provided credentials are for an admin login
    def is_admin_login(self, email, password):
        """
        Check if the provided credentials are for an admin login.

        :param email: The email to check.
        :param password: The password to check.
        :return: True if the credentials are for an admin, False otherwise.
        """
        return self.user.is_admin_login(email, password)

    # Validate user credentials
    def validate_user(self, email, password):
        """
        Validate the user credentials by checking the email and password against the database.

        :param email: The email of the user.
        :param password: The password of the user.
        :return: The user document if the credentials are valid, None otherwise.
        """
        return self.user.validate_user(email, password)

    # Get user details by user ID
    def get_user_by_id(self, user_id):
        """
        Get user details by user ID.

        :param user_id: The ID of the user.
        :return: The user document if found, None otherwise.
        """
        return self.user.get_user_by_id(user_id)

    # Add a sentence to the sentences collection
    def add_sentence(self, field, sentence):
        """
        Add a sentence to the specified field in the sentences collection.

        :param field: The field to add the sentence to.
        :param sentence: The sentence to add.
        """
        self.sentences_collection.add_sentence(field, sentence)

    # Update the fields for an insurance company
    def update_insurance(self, insurance_name, fields):
        """
        Update the fields for an insurance company.

        :param insurance_name: The name of the insurance company.
        :param fields: The fields to update or add.
        """
        self.insurances_collection.update_insurance(insurance_name, fields)

    # Update actions for an insurance company
    def update_actions(self, insurance_name, actions_data):
        """
        Update actions for an insurance company.

        :param insurance_name: The name of the insurance company.
        :param actions_data: The actions data to update.
        """
        self.actions_collection.update_actions(insurance_name, actions_data)

    # Insert individual data into the individual collection
    def insert_individual(self, json_data):
        """
        Insert individual data into the individual collection.

        :param json_data: The data to insert.
        """
        self.individual_collection.insert_individual(json_data)

    # Get individual collection documents by UUID
    def get_individual_collection_by_uuid(self, uuid):
        """
        Get individual collection documents by UUID.

        :param uuid: The UUID to search for.
        :return: A cursor to the documents that match the UUID.
        """
        return self.individual_collection.findall_query({"uuid": uuid})

    # Get individual collection document by insurance name
    def get_individual_collection_by_name(self, insurance_name):
        """
        Get individual collection document by insurance name.

        :param insurance_name: The name of the insurance company.
        :return: The document if found, None otherwise.
        """
        return self.individual_collection.find_one({insurance_name: {"$exists": True}})

    # Update individual data in the individual collection
    def update_individual(self, insurance_name, updated_fields):
        """
        Update individual data in the individual collection.

        :param insurance_name: The name of the insurance company.
        :param updated_fields: The fields to update.
        """
        self.individual_collection.update_individual(insurance_name, updated_fields)

     # Delete individual data from the individual collection
    def delete_individual(self, insurance_name):
        """
        Delete individual data from the individual collection.

        :param insurance_name: The name of the insurance company.
        """
        self.individual_collection.delete_individual(insurance_name)

    # Delete insurance data from the insurances collection
    def delete_insurance(self, insurance_name):
        """
        Delete insurance data from the insurances collection.

        :param insurance_name: The name of the insurance company.
        """
        self.insurances_collection.delete_one({insurance_name: {"$exists": True}})

    # Delete actions data from the actions collection
    def delete_actions(self, insurance_name):
        """
        Delete actions data from the actions collection.

        :param insurance_name: The name of the insurance company.
        """
        self.actions_collection.delete_one({insurance_name: {"$exists": True}})

    # Get all individual collection documents
    def get_all_individual_collections(self):
        """
        Get all individual collection documents.

        :return: A cursor to all documents in the individual collection.
        """
        return self.individual_collection.findall()

    # Generate a word cloud from the sentences collection ( FOR FUTURE WORK ONLY)
    def generate_wordcloud(self):
        """
        Generate a word cloud from the sentences collection.

        :return: A base64 encoded image of the word cloud.
        """
        return self.sentences_collection.generate_wordcloud()

     # Get the distribution of callbacks from the actions collection
    def get_callback_distribution(self):
        """
        Get the distribution of callbacks from the actions collection.

        :return: A dictionary with the count of each callback type.
        """
        return self.actions_collection.get_callback_distribution()

    # Check if an insurance company exists in the individual collection
    def check_insurance_exists(self, insurance_company):
        """
        Check if an insurance company exists in the individual collection.

        :param insurance_company: The name of the insurance company.
        :return: True if the insurance company exists, False otherwise.
        """
        return self.individual_collection.check_insurance_exists(insurance_company)

    def remove_field_from_insurance(self, insurance_name, field):
        """
        Remove a field from the insurances collection.

        :param insurance_name: The name of the insurance company.
        :param field: The field to remove.
        """
        self.insurances_collection.update_one(
            {"_id": insurance_name},
            {"$unset": {f"fields.{field}": ""}}
        )
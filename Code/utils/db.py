# Import the MongoClient class from the pymongo library
from pymongo import MongoClient
# Import configuration variables
from .config import MONGO_HOST, MONGO_PORT, DIALCONNECT_DB_NAME, USER_AUTH_DB_NAME

# DBManager class to handle database connections and operations
class DBManager:
    """
    A class to handle database connections and operations for MongoDB.
    """
    def __init__(self):
        """
        Initialize the DBManager with MongoDB client and databases.
        """
        # Initialize the MongoDB client with the provided host and port
        self.client = MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}/')
        # Initialize the DialConnect database
        self.dialconnect_db = self.client[DIALCONNECT_DB_NAME]
        # Initialize the User Authentication database
        self.user_auth_db = self.client[USER_AUTH_DB_NAME]

    # Method to get a collection from the appropriate database
    def get_collection(self, collection_name):
        """
        Get a collection from the appropriate database based on the collection name.

        :param collection_name: The name of the collection to retrieve.
        :return: The collection object.
        :raises ValueError: If the collection name is unknown.
        """
        # Check which database the collection belongs to and return the collection
        if collection_name in ['sentences', 'insurances', 'actions', 'individual']:
            return self.dialconnect_db[collection_name]
        elif collection_name == 'users':
            return self.user_auth_db[collection_name]
        else:
            # Raise an error if the collection name is unknown
            raise ValueError(f"Unknown collection: {collection_name}")

    # String representation of the DBManager instance
    def __str__(self):
        """
        Provide a string representation of the DBManager instance.

        :return: A string representation of the DBManager instance.
        """
        return f"DBManager(host={MONGO_HOST}, port={MONGO_PORT}, dialconnect_db={DIALCONNECT_DB_NAME}, user_auth_db={USER_AUTH_DB_NAME})"
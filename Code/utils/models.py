# Importing Libraries
from abc import ABC, abstractmethod
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import io
import base64
from .db import DBManager
from .config import MONGO_HOST, MONGO_PORT, DIALCONNECT_DB_NAME, USER_AUTH_DB_NAME

# User class to handle user-related operations
class User:
    """
    A class to handle user-related operations such as registration, validation, and admin login.
    """

    def __init__(self, db_manager):
        """
        Initialize the User class with a database manager.

        :param db_manager: An instance of DBManager to interact with the database.
        """
        self.db_manager = db_manager
        self.users_collection = db_manager.get_collection('users')

    # Check if an email is already registered
    def is_email_registered(self, email):
        """
        Check if an email is already registered in the database.

        :param email: The email to check.
        :return: True if the email is registered, False otherwise.
        """
        return self.users_collection.find_one({"email": email}) is not None

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
        self.users_collection.insert_one({
            "name": name,
            "email": email,
            "password": password,
            "organization": organization,
            "status": "user",
            "designation": designation
        })

    # Check if the provided credentials are for an admin login
    def is_admin_login(self, email, password):
        """
        Check if the provided credentials are for an admin login.

        :param email: The email to check.
        :param password: The password to check.
        :return: True if the credentials are for an admin, False otherwise.
        """
        return email == "super@rcm.com" and password == "12345"

    # Validate user credentials
    def validate_user(self, email, password):
        """
        Validate the user credentials by checking the email and password against the database.

        :param email: The email of the user.
        :param password: The password of the user.
        :return: The user document if the credentials are valid, None otherwise.
        """
        user = self.users_collection.find_one({"email": email})
        if user and user["password"] == password:
            return user
        return None

    # Get user details by user ID
    def get_user_by_id(self, user_id):
        """
        Get user details by user ID.

        :param user_id: The ID of the user.
        :return: The user document if found, None otherwise.
        """
        return self.users_collection.find_one({"_id": ObjectId(user_id)})


# Abstract base class for handling collections
class CollectionHandler(ABC):
    """
    An abstract base class for handling database collections.
    """
    def __init__(self, collection):
        """
        Initialize the CollectionHandler with a specific collection.

        :param collection: The collection to interact with.
        """
        # Initialize the collection
        self.collection = collection

    @abstractmethod
    def find_one(self, query):
        """
        Find one document that matches the query.

        :param query: The query to match documents against.
        :return: The first document that matches the query, or None if no match is found.
        """
        pass

    @abstractmethod
    def findall_query(self, query):
        """
        Find all documents that match the query.

        :param query: The query to match documents against.
        :return: A cursor to the documents that match the query.
        """
        pass

    @abstractmethod
    def findall(self):
        """
        Find all documents in the collection.

        :return: A cursor to all documents in the collection.
        """
        pass

    @abstractmethod
    def update_one(self, filter, update, upsert=False):
        """
        Update one document that matches the filter.

        :param filter: The filter to match documents against.
        :param update: The update to apply to the matched document.
        :param upsert: If True, insert the document if no match is found.
        :return: The result of the update operation.
        """
        pass

    @abstractmethod
    def insert_one(self, document):
        """
        Insert one document into the collection.

        :param document: The document to insert.
        :return: The result of the insert operation.
        """
        pass

    @abstractmethod
    def delete_one(self, query):
        """
        Delete one document that matches the query.

        :param query: The query to match documents against.
        :return: The result of the delete operation.
        """
        pass

# Class for handling sentences collection
class SentencesCollection(CollectionHandler):
    """
    A class for handling the sentences collection, which stores various sentences.
    """

    def find_one(self, query):
        return self.collection.find_one(query)

    def findall_query(self, query):
        return self.collection.find(query)

    def findall(self):
        return self.collection.find()

    def update_one(self, filter, update, upsert=False):
        return self.collection.update_one(filter, update, upsert=upsert)

    def insert_one(self, document):
        return self.collection.insert_one(document)

    def delete_one(self, query):
        return self.collection.delete_one(query)

    # Add a sentence to the collection
    def add_sentence(self, field, sentence):
        """
        Add a sentence to the specified field in the collection.

        :param field: The field to add the sentence to.
        :param sentence: The sentence to add.
        :return: The result of the update operation.
        """
        existing_sentences = self.find_one({"_id": "default"})
        if existing_sentences and field in existing_sentences:
            if sentence not in existing_sentences[field]:
                return self.update_one(
                    {"_id": "default"},
                    {"$addToSet": {field: sentence}},
                    upsert=True
                )
        else:
            return self.update_one(
                {"_id": "default"},
                {"$set": {field: [sentence]}},
                upsert=True
            )

    # Remove duplicate sentences from the collection
    def remove_duplicates(self):
        """
        Remove duplicate sentences from the collection.
        """
        existing_sentences = self.find_one({"_id": "default"})
        if existing_sentences:
            for field, sentences in existing_sentences.items():
                if field != "_id":
                    unique_sentences = list(set(sentences))
                    self.update_one(
                        {"_id": "default"},
                        {"$set": {field: unique_sentences}},
                        upsert=True
                    )

    # Get all sentences from the collection
    def get_sentences(self):
        """
        Get all sentences from the collection.

        :return: A list of all sentences in the collection.
        """
        sentences_doc = self.find_one({"_id": "default"})
        sentences = []
        for field, field_sentences in sentences_doc.items():
            if field != "_id":
                sentences.extend(field_sentences)
        return sentences

    # Generate a word cloud from the sentences (For Future WORK ONLYY)
    def generate_wordcloud(self):
        """
        Generate a word cloud from the sentences in the collection.

        :return: A base64 encoded image of the word cloud.
        """
        sentences = self.get_sentences()
        text = " ".join(sentences)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        img = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(img, format='png')
        img.seek(0)
        img_base64 = base64.b64encode(img.getvalue()).decode()
        return img_base64

# Class for handling insurances collection
class InsurancesCollection(CollectionHandler):
    """
    A class for handling the insurances collection, which stores insurance company data.
    """

    def find_one(self, query):
        return self.collection.find_one(query)

    def findall_query(self, query):
        return self.collection.find(query)

    def findall(self):
        return self.collection.find()

    def update_one(self, filter, update, upsert=False):
        return self.collection.update_one(filter, update, upsert=upsert)

    def insert_one(self, document):
        return self.collection.insert_one(document)

    def delete_one(self, query):
        return self.collection.delete_one(query)

    # Update the fields for an insurance company
    def update_insurance(self, insurance_name, fields):
        """
        Update the fields for an insurance company.

        :param insurance_name: The name of the insurance company.
        :param fields: The fields to update or add.
        :return: The result of the update operation.
        """
        existing_fields = self.find_one({insurance_name: {"$exists": True}})
        if existing_fields and insurance_name in existing_fields:
            existing_fields = existing_fields[insurance_name]
            for field in fields:
                if field not in existing_fields:
                    existing_fields.append(field)
            fields = existing_fields
        return self.update_one(
            {insurance_name: {"$exists": True}},
            {"$set": {insurance_name: fields}},
            upsert=True
        )

# Class for handling actions collection
class ActionsCollection(CollectionHandler):
    """
    A class for handling the actions collection, which stores actions related to insurance companies.
    """

    def find_one(self, query):
        return self.collection.find_one(query)

    def findall_query(self, query):
        return self.collection.find(query)

    def findall(self):
        return self.collection.find()

    def update_one(self, filter, update, upsert=False):
        return self.collection.update_one(filter, update, upsert=upsert)

    def insert_one(self, document):
        return self.collection.insert_one(document)

    def delete_one(self, query):
        return self.collection.delete_one(query)

    # Update actions for an insurance company
    def update_actions(self, insurance_name, actions_data):
        """
        Update actions for an insurance company.

        :param insurance_name: The name of the insurance company.
        :param actions_data: The actions data to update.
        :return: The result of the update operation.
        """
        return self.update_one(
            {insurance_name: {"$exists": True}},
            {"$set": {insurance_name: actions_data}},
            upsert=True
        )

    # Get the distribution of callbacks
    def get_callback_distribution(self):
        """
        Get the distribution of callbacks in the actions collection.

        :return: A dictionary with the count of each callback type.
        """
        callbacks = {"send_dtmf": 0, "send_audio_words": 0}
        for document in self.findall():
            for key, value in document.items():
                if key != "_id":
                    for sub_key, sub_value in value.items():
                        callback = sub_value.get("callback")
                        if callback in callbacks:
                            callbacks[callback] += 1
        return callbacks

# Class for handling individual collection
class IndividualCollection(CollectionHandler):
    """
    A class for handling the individual collection, which stores individual data related to insurance companies.
    """

    def find_one(self, query):
        return self.collection.find_one(query)

    def findall_query(self, query):
        return self.collection.find(query)

    def findall(self):
        return self.collection.find()

    def update_one(self, filter, update, upsert=False):
        return self.collection.update_one(filter, update, upsert=upsert)

    def insert_one(self, document):
        return self.collection.insert_one(document)

    def delete_one(self, query):
        return self.collection.delete_one(query)

    # Insert individual data into the collection
    def insert_individual(self, json_data):
        """
        Insert individual data into the collection.

        :param json_data: The data to insert.
        :return: The result of the insert operation.
        """
        return self.insert_one(json_data)

    # Update individual data in the collection
    def update_individual(self, insurance_name, updated_fields):
        """
        Update individual data in the collection.

        :param insurance_name: The name of the insurance company.
        :param updated_fields: The fields to update.
        :return: The result of the update operation.
        """
        return self.update_one(
            {insurance_name: {"$exists": True}},
            {"$set": {insurance_name: updated_fields}}
        )

    # Delete individual data from the collection
    def delete_individual(self, insurance_name):
        """
        Delete individual data from the collection.

        :param insurance_name: The name of the insurance company.
        :return: The result of the delete operation.
        """
        return self.delete_one({insurance_name: {"$exists": True}})

    # Check if an insurance company exists in the collection
    def check_insurance_exists(self, insurance_company):
        """
        Check if an insurance company exists in the collection.

        :param insurance_company: The name of the insurance company.
        :return: True if the insurance company exists, False otherwise.
        """
        # Query the database to check if the insurance company exists
        query = {
            insurance_company: {"$exists": True}
        }
        result = self.find_one(query)
        return result is not None
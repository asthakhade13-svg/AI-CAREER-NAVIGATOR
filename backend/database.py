from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: MongoClient = None
    db = None

    @classmethod
    def connect_db(cls):
        try:
            cls.client = MongoClient(settings.MONGODB_URI)
            # Verify connection
            cls.client.admin.command('ping')
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise e

    @classmethod
    def close_db(cls):
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed.")

    @classmethod
    def get_collection(cls, collection_name: str):
        if cls.db is None:
            raise Exception("Database is not connected. Call connect_db() first.")
        return cls.db[collection_name]

db = Database()
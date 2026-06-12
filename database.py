from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    client: MongoClient = None
    db = None
    is_connected: bool = False

    @classmethod
    def connect_db(cls):
        try:
            cls.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=3000  # 3 second timeout, not 30s
            )
            # Verify connection
            cls.client.admin.command('ping')
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            cls.is_connected = True
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            cls.is_connected = False
            logger.warning(
                f"MongoDB not available — running without database. "
                f"Quiz/ML features will still work. Error: {type(e).__name__}"
            )

    @classmethod
    def close_db(cls):
        if cls.client:
            cls.client.close()
            cls.is_connected = False
            logger.info("MongoDB connection closed.")

    @classmethod
    def get_collection(cls, collection_name: str):
        if not cls.is_connected or cls.db is None:
            logger.warning(
                f"MongoDB not connected — skipping collection access for '{collection_name}'"
            )
            return None
        return cls.db[collection_name]


db = Database()
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Load the .env file
load_dotenv()

# Get the Mongo URI from .env
uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("❌ Error connecting to MongoDB:", e)
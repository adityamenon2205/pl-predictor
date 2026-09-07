import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "pl_predictor")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in the environment")

client = MongoClient(MONGODB_URI)

db = client[MONGODB_DATABASE]
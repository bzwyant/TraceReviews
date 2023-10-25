from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class ReportsDatabase(object):
    def __init__(self, username, password):
        uri = f"mongodb+srv://{username}:{password}@trace.gqna2hn.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.database = self.client['reports']
from pymongo  import ASCENDING, DESCENDING
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorClient
import json


def create_client(uri) -> MongoClient:
    return MongoClient(uri, server_api=ServerApi('1'))

def get_course_info_batch(client: MongoClient, database_name: str, collection_name: str, batch_size: int):
    db = client[database_name]
    collection = db[collection_name]

    last_id_seen = 0

    while last_id_seen != -1:
        cursor = collection.find({"courseId": {"$gt": last_id_seen}}).sort('courseId', ASCENDING).limit(batch_size)
        result = list(cursor)
        
        # Convert ObjectId values to strings in the result
        for doc in result:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])

        last_id_seen = result[-1].get("courseId", -1) if result else -1
        # print(last_id_seen)
        # json_result = json.dumps(result, indent=2)
        # yield json_result

        yield result

def create_async_client(uri) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(uri)

async def get_course_info_batch(client: AsyncIOMotorClient, database_name: str, collection_name: str, batch_size: int):
    db = client[database_name]
    collection = db[collection_name]

    last_id_seen = 0

    while last_id_seen != -1:
        cursor = collection.find({"courseId": {"$gt": last_id_seen}}).sort('courseId', ASCENDING).limit(batch_size)
        result = await cursor.to_list(length=None)

        if not result:
            return
        
        for doc in result:
            print(doc)

        exit()

        # Convert ObjectId values to strings in the result
        for doc in result:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])

        last_id_seen = result[-1].get("courseId", -1) if result else -1

        yield result
import pymongo
from pymongo import MongoClient

class Database(object):
    """
    Describe: This class using to connect to mongodb
    Output common: all method of this class will return a dict with 3 keys:
        - success(boolean): result of method(success of fail)
        - object: object return if result of method is success
        - message: error message if result of method is fail
    """
    def __init__(self, collection_name):
        self.client = MongoClient(maxPoolSize=None)
        self.db = self.client.word_recognition
        if collection_name == 'bigram_collection':
            self.collection = self.db.bigram_collection
        elif collection_name == 'sentence_collection':
            self.collection = self.db.sentence_collection
        else:
            self.collection = self.db.word_collection

    def create(self, object_info):
        """
        Usage: This function will create object with object info and add it to mongodb
        Params:
            - object_info(dict): A dict of info object
        Output: follow the common output
        """
        try:
            new_object_id = self.collection.insert_one(object_info).inserted_id
            return {
                'success': True,
                'object': new_object_id
            }
        except Exception as error:
            return {
                'success': False,
                'message': str(error)
            }

    def create_bulk(self, object_infos):
        """
        Usage: This function will create object with object info and add it to mongodb
        Params:
            - object_infos(array of dict): An array of dict of info object
        Output: follow the common output
        """
        try:
            new_object_ids = self.collection.insert_many(object_infos)
            new_object_ids = new_object_ids.inserted_ids
            return {
                'success': True,
                'object': new_object_ids
            }
        except Exception as error:
            return {
                'success': False,
                'message': str(error)
            }


    def find_one(self, object_info):
        """
        Usage: This function will find one object with object info and add it to mongodb
        Params:
            - object_info(dict): A dict of info object want to find
        Output: follow the common output
        """
        try:
            object_find = self.collection.find_one(object_info)
            return {
                'success': True,
                'object': object_find
            }
        except Exception as error:
            return {
                'success': False,
                'message': str(error)
            }

    def where(self, object_info):
        """
        Usage: This function will find all object with object info and add it to mongodb
        Params:
            - object_info(dict): A dict of info object want to find
        Output: follow the common output
        """
        try:
            object_finds = self.collection.find(object_info)
            return {
                'success': True,
                'object': object_finds
            }
        except Exception as error:
            return {
                'success': False,
                'message': str(error)
            }

    def update(self, object_info, update_info):
        """
        Usage: This function will update object find in object info and update it to update_info
            (override)
        Params:
            - object_info(dict): A dict of info object want to find to update
            - update_info(dict): A dict of info will update
        Output: follow the common output
        """
        try:
            update_object = self.collection.update(
                object_info,
                { '$set': update_info },
                upsert=False
            )
            return {
                'success': True,
            }
        except Exception as error:
            return {
                'success': False
            }


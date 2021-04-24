import os
from bson import json_util, ObjectId
import json



# function to query all recipe from database

def all_recipe_controller_home(filters, db_conn, host_url):
    print("from all recipe...")
    print("filter :", filters)
    try:
        result = db_conn["recipes"].find(
            filters).sort("createdOn", -1).limit(9)
        recipe_list = map_response(result, host_url)
        return recipe_list
    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}



def all_recipe_controller(filters, db_conn, host_url):
    print("from all recipe...")
    print("filter :", filters)
    try:
        result = db_conn["recipes"].find(filters).sort("createdOn", -1)
        recipe_list = map_response(result, host_url)
        return recipe_list
    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}
        

# functions to add recipe to database
def add_recipe_controller(payload, db_conn):
    try:
        result = db_conn["recipes"].insert_one(payload)
        print(result.inserted_id)
        print(result.acknowledged)
        return {
            "success": True,
            "message": "Recipe created successfully",
        }

    except Exception as e:
        return {"success": False, "message": "Error in api: " + str(e)}


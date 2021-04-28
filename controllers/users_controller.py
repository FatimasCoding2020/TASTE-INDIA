from pprint import pprint
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash


def signup_controller(payload, db_conn):
    """
    Function to signup a user
    """
    try:
        # validate email if it already exists
        email_check = db_conn["users"].find_one({"email": payload["email"]})

        if email_check is None:
            password = payload["password"]
            payload["password"] = generate_password_hash(password)
            # role mapping
            pprint(payload)
            # insert the user
            result = db_conn["users"].insert_one(payload)
            return {
                "success": True,
                "message": "User created successfully",
                "_id": result.inserted_id,
            }
        else:
            return {"success": False, "message": "User already exists"}
    except Exception as e:
        return {"success": False, "message": "Error in api: " + str(e)}


def login_controller(payload, db_conn):
    """
    The function to validate a user tyring to login into the website
    """
    try:
        user_data = db_conn["users"].find_one({"email": payload["email"]})
        if user_data:

            if check_password_hash(
                    user_data.get("password"),
                    payload.get("password")):
                return {
                    "success": True,
                    "message": "successfully logged in..",
                    "_id": str(user_data.get("_id")),
                }
            else:
                return {"success": False, "message": "Incorrect Password"}

        else:
            return {"success": False, "message": "User does not exist"}
    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}


def get_user_name(userid, db_conn):
    """
    Finding a username based on the userid from the database
    """
    user_data = db_conn["users"].find_one({"_id": ObjectId(userid)})
    return user_data["username"]

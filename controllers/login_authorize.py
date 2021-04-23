import jwt
from jwt.exceptions import DecodeError


# login  of user is verified by querying by email and id is returned
def login_authorize(request, db_conn):
    try:
        if "Cookie" in request.headers:
            cookies = request.headers["Cookie"]
            logintoken = (
                cookies.split("logintoken=")[1].split(";")[0]
                if "logintoken" in cookies
                else "notoken"
            )
            token_data = jwt.decode(logintoken, "SECRET", algorithms="HS256")
            token_email = token_data["email"]
            user_data = db_conn["users"].find_one({"email": token_email})
            if user_data is None:
                return {"success": False, "_id": None}
            email = user_data["email"]
            if token_email == str(email):
                return {
                    "success": True,
                    "_id": str(user_data["_id"]),
                    "name": user_data["username"],
                }
        else:
            return {"success": False, "_id": None}
    except ValueError:
        return {"success": False, "_id": None}
    except DecodeError:
        return {"success": False, "_id": None}

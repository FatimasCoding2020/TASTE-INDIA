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


def map_response(data, host_url):
    try:
        result = []
        for d in data:
            # print("id", str(d['_id']))
            d["ratings"] = 0 if d["ratings"] is None else d["ratings"]
            result.append(
                {
                    "id": str(d["_id"]),
                    "userid": str(d["userId"]),
                    "recipeName": d["recipeName"],
                    "createdOn": str(d["createdOn"]).split(" ")[0],
                    "category": d["category"][0],
                    "description": str(
                        d["description"]
                    ).replace("\r", "").split("\n"),
                    "imageUrl": host_url + d["imageUrl"]
                    if "static" in d["imageUrl"]
                    else d["imageUrl"],
                    "cookingTime": d["cookingTime"],
                    "preprationTime": d["preprationTime"],
                    "servings": str(
                        d["servings"]
                    ).replace("\r", "").split("\n"),
                    "ingredients": str(
                        d["ingredients"]
                    ).replace("\r", "").split("\n"),
                    "instructions": str(d["instructions"])
                        .replace("\r", "")
                        .split("\n"),
                    "tips": str(d["tips"]).replace("\r", "").split("\n"),
                    "ratings": d["ratings"],
                    "rating_count": [i for i in range(
                        1, int(d["ratings"]) + 1)]
                    if d["ratings"] > 0
                    else [],
                    "without_rating": [i for i in range(
                        int(d["ratings"]) + 1, 6)]
                    if d["ratings"] > 0
                    else [1, 2, 3, 4, 5],
                    "hasrating": True if d["ratings"] > 0 else False,
                    "isFavourate": d["isFavourate"],
                }
            )
        return result
    except Exception as e:
        print("error--e", e)
        return []

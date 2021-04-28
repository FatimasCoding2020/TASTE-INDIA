from .recipe_controller import map_response


def single_recipe_controller(filters, db_conn, host_url):
    """
    This function is to query a single recipe from database
    """
    try:
        result = db_conn["recipes"].find(filters).sort("createdOn", -1)
        recipe_list = map_response(result, host_url)
        return recipe_list

    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}


def get_category_recipe(filters, db_conn, host_url):
    """
    This function queries database recipe by categories
    """
    try:
        result = db_conn["recipes"].find(
            filters).sort("createdOn", -1).limit(9)
        recipe_list = map_response(result, host_url)

        return recipe_list

    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}

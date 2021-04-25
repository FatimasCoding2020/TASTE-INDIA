from controllers.recipe_controller import map_response
import pandas as pd


def get_stats(db_conn, host_url):
    print("from get_stats...")
    try:
        # getting user counts
        users_count = db_conn["users"].find({}).count()

        # getting recipe counts
        recipies = db_conn["recipes"].find({})
        response = map_response(recipies, host_url)
        df = pd.DataFrame(response)
        df_grouped = df.groupby("category").count()
        df_grouped = df_grouped[["recipeName"]].reset_index().to_dict("r")
        result = {
            "success": True,
            "total_users": users_count,
            "total_recipes": recipies.count(),
            "recipe_data": [
                i for i in df_grouped if i["category"] != "SELECT CATEGORY"
            ],
        }
        return result

    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}

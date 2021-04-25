import os
from datetime import datetime, timedelta
import random
import string
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
)
from werkzeug.utils import secure_filename
import jwt
from database import db
from controllers.login_authorize import login_authorize
from controllers.recipe_controller import *
from controllers.users_controller import *
from controllers.categories_controller import *
from controllers.stats_controller import *

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(APP_ROOT, "static/uploaded_images")



# generating random striing
def randstr():
    return "".join(
        random.choice(
            string.ascii_lowercase +
            string.digits) for _ in range(10))


@app.route("/", methods=["GET"])
def home():
    try:
        print("_______________________________", request.host_url)
        login_data = login_authorize(request, db)
        # if login is unsuccessfull redirecting to login page again
        islogin = True if login_data["success"] else False
        response = all_recipe_controller_home(
            {}, db_conn=db, host_url=request.host_url)
        return render_template("index.html", result=response, islogin=islogin)

    except BaseException:

        return render_template("error_handlers/error.html")


@app.route("/shop")
def shop():
    try:
        # checking for user login status  if not  then redirecting to login
        # page
        login_data = login_authorize(request, db)
        if not login_data["success"]:
            return redirect(url_for("login"))
        return render_template("misc/shop.html")
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    try:
        if request.method == "POST":
            checkbox = (request.form.get("checkbox")
                        if "checkbox" in request.form else "off")

            if checkbox == "off":
                error = "Please select terms & condition and proceed"
                return render_template("users/signup.html", error=error)

            payload = dict(
                email=request.form["email"],
                username=request.form["username"],
                password=request.form["password"],
                creadedOn=datetime.now(),
            )
            response = signup_controller(payload=payload, db_conn=db)
            print("response----------------------------", response)
            if response["success"]:
                return redirect(url_for("login"))
            else:
                error = "User already exists"
                return render_template("users/signup.html", error=error)

        return render_template("users/signup.html")
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            checkbox = (request.form.get("checkbox")
                        if "checkbox" in request.form else "off")

            if checkbox == "off":
                error = "Please select terms & condition and proceed"
                return render_template("users/login.html", error=error)
            # getting payload from login form
            print(request.form)
            payload = dict(
                email=request.form["email"],
                password=request.form["password"],
            )
            # verifying the user login
            response = login_controller(payload, db)
            print("user login verified", response)
            if response["success"]:
                # creating the JWT token for user session
                print("creating JWT token")
                encode = jwt.encode(
                    {
                        "iat": datetime.now(),
                        "email": payload["email"],
                        "exp": datetime.now() + timedelta(days=3),
                    },
                    "SECRET",
                    algorithm="HS256",
                )
                # print("encode--------------------",encode)
                resp = make_response(redirect(url_for("profile")))
                # token = str(encode).split("'")[1]
                print("token---------------", encode)
                # setting cookie using lofin token
                resp.set_cookie("logintoken", encode)
                return resp
            else:
                error = "Your email or password didn't match"
                return render_template("users/login.html", error=error)

        return render_template("users/login.html")
    except Exception as e:
        print("error ------------------", e)
        return render_template("error_handlers/error.html")


@app.route("/profile")
def profile():
    try:
        login_data = login_authorize(request, db)
        # print(login_data)
        # if login is unsuccessfull redirecting to login page again
        if not login_data["success"]:
            return redirect(url_for("login"))

        payload_filter = {"userId": login_data["_id"]}
        response = all_recipe_controller(
            payload_filter, db_conn=db, host_url=request.host_url)
        print("response---", response)
        return render_template(
            "users/myaccount.html",
            name=login_data["name"],
            result=response)
    except Exception as e:
        print("error----------------------------------", e)


@app.route("/logout")
def logout():
    try:
        # expering token for logout
        resp = make_response(redirect(url_for("login")))
        resp.set_cookie("logintoken", expires=0)
        return resp
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/addrecipes", methods=["GET", "POST"])
def add_recipes():
    try:
        print("from add recipes...")
        # validating user before adding recipe
        login_data = login_authorize(request, db)
        print(login_data)
        # if login is unsuccessfull redirecting to login page again
        if not login_data["success"]:
            return redirect(url_for("login"))
        # we user is logged in reading user input from form
        if request.method == "POST":
            # reading the imade file
            image = request.files["imagefile"]
            # reading image url
            imagelink = request.form.get("imageurl")
            # when image filename is available saving the uploaded image file
            # to /static/uploaded_images/ directory
            if len(image.filename) != 0:
                image_file = secure_filename(randstr() + "-" + image.filename)
                image.save(os.path.join(IMAGE_DIR, image_file))
                imagelink = "/static/uploaded_images/" + str(image_file)
            # creating payload dictonary from form to save to database
            payload = dict(
                recipeName=request.form.get("recepiename", None),
                category=request.form.getlist("category", None),
                description=request.form.get("description", None),
                imageUrl=imagelink,
                servings=request.form.get("servings", None),
                preprationTime=request.form.get("preparationtime", None),
                cookingTime=request.form.get("cookingtime", None),
                ingredients=request.form.get("ingredients", None),
                instructions=request.form.get("instructions", None),
                tips=request.form.get("tips", None),
                userId=login_data["_id"],
                createdOn=datetime.now(),
                isFavourate=False,
                ratings=request.form.get("ratings", 0),
            )
            response = add_recipe_controller(payload=payload, db_conn=db)

            # print("response---------", response)
            return redirect(url_for("profile"))

        return render_template("recipes/addrecipes.html")
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/updaterecipe/<recipieid>", methods=["GET", "POST"])
def update_recipe(recipieid):
    try:
        print("from update recipe...")
        # validating user before adding recipe
        login_data = login_authorize(request, db)
        print(login_data)
        # if login is unsuccessfull redirecting to login page again
        if not login_data["success"]:
            return redirect(url_for("login"))

        response = single_recipe_controller(
            {"_id": ObjectId(recipieid)}, db, request.host_url)[0]
        response["servings"] = "\n".join(response["servings"])
        response["description"] = "\n".join(response["description"])
        response["ingredients"] = "\n".join(response["ingredients"])
        response["instructions"] = "\n".join(response["instructions"])
        response["tips"] = "\n".join(response["tips"])
        if request.method == "POST":
            image = request.files["imagefile"]
            # reading image url
            imagelink = request.form.get("imageurl")
            imagelink = (
                "/static/uploaded_images/" + str(imagelink).split("/")[-1]
                if "static" in imagelink
                else imagelink
            )
            # when image filename is available saving the uploaded image file
            # to /static/uploaded_images/ directory
            if len(image.filename) != 0:
                image_file = secure_filename(randstr() + "-" + image.filename)
                image.save(os.path.join(IMAGE_DIR, image_file))
                imagelink = "/static/uploaded_images/" + str(image_file)
            query = {"_id": ObjectId(recipieid)}
            update = dict(
                recipeName=request.form.get("recepiename", None),
                category=request.form.getlist("category", None),
                description=request.form.get("description", None),
                imageUrl=imagelink,
                servings=request.form.get("servings", None),
                preprationTime=request.form.get("preparationtime", None),
                cookingTime=request.form.get("cookingtime", None),
                ingredients=request.form.get("ingredients", None),
                instructions=request.form.get("instructions", None),
                tips=request.form.get("tips", None),
                userId=login_data["_id"],
                updatedOn=datetime.now(),
                isFavourate=request.form.get("isFavourate", None),
            )
            db["recipes"].update_one(query, {"$set": update})
            print("Recipe updated successfully!")
            return redirect(url_for("profile"))

        return render_template(
            "recipes/editrecipe.html",
            result=response,
            hasresult=True)
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/deleterecipe/<recipieid>", methods=["GET"])
def delete_recipe(recipieid):
    try:
        print("from delete recipe...")
        # validating user before adding recipe
        login_data = login_authorize(request, db)
        print(login_data)
        # if login is unsuccessfull redirecting to login page again
        if not login_data["success"]:
            return redirect(url_for("login"))
        directory = os.getcwd()
        response = db["recipes"].find_one({"_id": ObjectId(recipieid)})
        db["recipes"].delete_one({"_id": ObjectId(recipieid)})
        print("image url -------", response["imageUrl"])
        if os.path.exists(directory + response["imageUrl"]):
            os.remove(directory + response["imageUrl"])

        print("Recipe deleted successfully!")
        return redirect(url_for("profile"))
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/single_recipes/<recipieid>")
def single_recipes(recipieid):
    try:
        login_data = login_authorize(request, db)
        # if login is unsuccessfull redirecting to login page again
        islogin = True if login_data["success"] else False
        # this API only gives one output
        payload_filter = dict({"_id": ObjectId(recipieid)})
        response = single_recipe_controller(
            payload_filter, db_conn=db, host_url=request.host_url)[0]
        if islogin:
            islogin = True if (
                response["userid"] == login_data["_id"]) else False
        # print("response :", response)
        response["username"] = get_user_name(response["userid"], db)

        return render_template(
            "recipes/single-recipes.html",
            result=response,
            hasresult=True,
            islogin=islogin)
    except Exception as e:
        print("Error-------------", e)
        return render_template("error_handlers/error.html")


@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    try:
        response = all_recipe_controller(
            {}, db_conn=db, host_url=request.host_url)
        # print("response :", response)
        return render_template("recipes/recipes.html", result=response, hasresult=True)
    except BaseException:
        return render_template("error_handlers/error.html")

# Note: below APIs for catogery filtering and same logic is used
# 1. user login status is checked if not logged,
# list out all  recipies on the catogery
# 2.else list out the recepies owned by users
@app.route("/rice")
def rice():
    try:
        response = get_category_recipe(
            {"category": "RICE"}, db_conn=db, host_url=request.host_url)
        return render_template("categories/rice.html", result=response, hasresult=True)

    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/vegetarian")
def vegetarian():
    try:
        response = get_category_recipe(
            {"category": "VEGETARIAN"}, db_conn=db, host_url=request.host_url)
        return render_template(
            "categories/vegetarian.html",
            result=response,
            hasresult=True)
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/nonvegetarian")
def non_vegetarian():
    try:

        response = get_category_recipe(
            {
                "category": "NON-VEGETARIAN"
                }, db_conn=db, host_url=request.host_url)
        return render_template(
            "categories/non-Vegetarian.html",
            result=response,
            hasresult=True)
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/desserts")
def desserts():
    try:
        response = get_category_recipe(
            {"category": "DESSERTS"}, db_conn=db, host_url=request.host_url)
        return render_template(
            "categories/desserts.html",
            result=response,
            hasresult=True)
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/snacks")
def snacks():
    try:

        response = get_category_recipe(
            {"category": "SNACKS"}, db_conn=db, host_url=request.host_url)
        return render_template("categories/snacks.html", result=response, hasresult=True)
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/drinks")
def drinks():
    try:
        response = get_category_recipe(
            {"category": "DRINKS"}, db_conn=db, host_url=request.host_url)
        return render_template("categories/drinks.html", result=response, hasresult=True)
    except BaseException:
        return render_template("error_handlers/error.html")


@app.route("/spicepantry")
def spicepentry():
    try:
        response = get_category_recipe(
            {
                "category": "SPICE-PANTRY"
                }, db_conn=db, host_url=request.host_url)
        return render_template(
            "categories/spicepentry.html",
            result=response,
            hasresult=True)
    except BaseException:
        return render_template("error_handlers/error.html")

@app.route("/term")
def term():
    return render_template("misc/term.html")


@app.route("/stats")
def stats():
    try:
        login_data = login_authorize(request, db)
        if not login_data["success"]:
            return redirect(url_for("login"))
        response = get_stats(db, request.host_url)
        return render_template("misc/stat.html", result=response)
    except BaseException:
        return render_template("error_handlers/error.html")


# Handling error 404 and displaying relevant web page
@app.errorhandler(404)
def not_found_error(error):
    return render_template("error_handlers/error.html"), 404


# @app.route("/myaccount")
# def method_name():
#     return render_template("myaccount.html")


@app.route("/search", methods=["POST"])
def search_api():
    if request.method == "POST":
        search_string = request.form.get("searchstring", "")

        if len(search_string) == 0:
            is_search = False
            return render_template("misc/search.html", is_search=is_search)
        collection_filter = {
            "$or": [
                {"recipeName": {"$regex": search_string, "$options": "i"}},
                {"category": {"$regex": search_string, "$options": "i"}},
                {"description": {"$regex": search_string, "$options": "i"}},
                {"ingredients": {"$regex": search_string, "$options": "i"}},
                {"instructions": {"$regex": search_string, "$options": "i"}},
            ]
        }
        print("collection_filter", collection_filter)
        response = db["recipes"].find(collection_filter)
        result = map_response(response, request.host_url)
        is_search = True if len(result) > 0 else False
        return render_template(
            "misc/search.html",
            result=result,
            is_search=is_search)


# test to insert data to the data base
@app.route("/subscription", methods=["POST"])
def subscribe():
    print("Inside Subscription API")
    try:
        if request.method == 'POST':
            payload = dict(
                email=request.form["email"],
            )
            user_data = db["subscription"].find_one(payload)
            if user_data:
                message = "Hi, You are already subscribed"
                return render_template("misc/subscription.html", message=message)
            else:
                message = "Hi, You are subscribed now"
                db["subscription"].insert_one(payload)
                return render_template("misc/subscription.html", message=message)

    except Exception as e:
        print(e)
        return render_template("error_handlers/error.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

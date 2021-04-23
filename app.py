import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
)
from database import db
from controllers.login_authorize import login_authorize
from controllers.recipe_controller import *
from controllers.users_controller import *
from datetime import datetime

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(APP_ROOT, "static/uploaded_images")


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

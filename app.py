import os
from flask import (
    Flask,
    render_template,
    request,
)
from database import db
from controllers.login_authorize import login_authorize
from controllers.recipe_controller import *


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

        return render_template("error.html")







if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

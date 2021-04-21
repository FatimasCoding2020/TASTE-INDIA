import os
from flask import (
    Flask,
    render_template,
)

from database import db



app = Flask(__name__)



app.secret_key = os.getenv("SECRET_KEY")
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(APP_ROOT, "static/uploaded_images")





@app.route("/", methods=["GET"])
def home():
    

    return render_template("index.html")





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

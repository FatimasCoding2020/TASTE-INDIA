import os
import pymongo
import dotenv
import traceback
import dns

try:
    dotenv.load_dotenv(".env")
    print((os.getenv("APP_ENV")))
    if (os.getenv("APP_ENV")) is None:
        print("env not found, quitting app....")
        #quit()
except Exception:
    error = traceback.print_exc()
    quit()
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client.get_database("taste_india")

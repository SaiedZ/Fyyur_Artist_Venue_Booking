from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# IMPLEMENT DATABASE URL -> DB_URI is stored in .env file
SQLALCHEMY_DATABASE_URI = os.environ['DB_URI']

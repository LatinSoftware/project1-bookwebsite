import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


DB_URL = "postgres://bqzkxfbmdqzmhg:781498301a0c633a9e1bfefcb56bb6a52716790052b60036e1a5b6edd5034e58@ec2-3-91-112-166.compute-1.amazonaws.com:5432/dfs65a0uphe416"

# Check for environment variable
if not create_engine(DB_URL):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(DB_URL)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"

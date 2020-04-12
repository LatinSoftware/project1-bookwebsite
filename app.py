import os

from flask import Flask, session,render_template, request
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
    return render_template("index.html")

# User Methods
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/register/create", methods=['POST'])
def create_user():
    # check if user has been register before
    email = request.form.get("email")
    name = request.form.get("name")
    passwd = request.form.get("password")
    if db.execute("SELECT id FROM users WHERE email = :email", {"email": email}).rowcount > 0:
        return render_template("register.html", message="User exist")
    # register
    db.execute("INSERT INTO users(name, email, password) VALUES(:name, :email, :password)",
    {"name": name, "email": email, "password": passwd})
    db.commit()
    return render_template("login.html")
   

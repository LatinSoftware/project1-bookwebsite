import os

from flask import Flask, session,render_template, request, redirect, url_for
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
    if session.get("user") is None:
        session["user"] = []

    return render_template("index.html", user=session["user"])

# User Methods
@app.route("/login", methods=['GET', 'POST'])
def login():

    error = ""
    if request.method == 'POST':
        email = request.form.get("email")
        passwd = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE email = :email AND password = :passwd", 
        {"email": email, "passwd": passwd}).fetchone()
        if user:
            session["user"].append(user)
            return redirect(url_for('index'))
        else:
            error = "Invalid username/password"
    
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route("/register", methods=['POST', 'GET'])
def register():
    message = ""
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        passwd = request.form.get("password")
        if db.execute("SELECT id FROM users WHERE email = :email", {"email": email}).rowcount > 0:
            message = "User Already Exist"
        else:
            db.execute("INSERT INTO users(username, email, password) VALUES(:name, :email, :password)",
            {"name": name, "email": email, "password": passwd})
            db.commit()
            return url_for("login")
    return render_template('register.html', message=message)
   
@app.route("/books")
def books():
    books = db.execute("SELECT id, title, author FROM books LIMIT 10")
    return render_template('books.html', all_b=books)

@app.route("/books/<int:book_id>")
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {'id': book_id}).fetchone()
    if book:
        reviews = db.execute("SELECT t2.username, t1.score, t1.comment FROM book_reviews as t1 INNER JOIN users as t2 ON t1.user_id = t2.id and t1.book_id = :book_id", 
        {"book_id": book_id})

        user_review = db.execute("SELECT id, score FROM book_reviews WHERE user_id = :user_id AND book_id = :book_id", 
        {"book_id": book_id, "user_id": session.get('user')[0]['id']}).fetchone()

        avg_score = db.execute("SELECT AVG(score) as score FROM book_reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchone()
        if avg_score.score:
            avg_score = int(avg_score.score)
        else:
            avg_score = 0
        return render_template("book.html", book=book, reviews=reviews, user_review=user_review, avg_score=avg_score)
    else:
        return "404 no found"
@app.route("/books/search", methods=["GET"])
def search():
    q = request.args.get("q")
    books = db.execute("SELECT id, title, author FROM books WHERE title LIKE '%:data:%' or author LIKE '%:data:%' or isbn LIKE '%:data:%'",
    {"data": q}).fetchall()
    print(books)
    return render_template('books.html', books=books)


@app.route('/book/comment/create', methods=['POST'])
def createComment():
    score = request.form.get('score')
    comment = request.form.get('comment')
    user_id = session.get('user')[0]['id']
    book_id = request.form.get('book_id')
    
    db.execute("INSERT INTO book_reviews(book_id,user_id,score,comment) VALUES(:book_id, :user_id, :score, :comment)",
    {
        'book_id': book_id,
        'user_id': user_id,
        'score': score,
        'comment': comment
    })
    if db.commit():
        return "True"
    else:
        return "False"
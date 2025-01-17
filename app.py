import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, string_word_count

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///serenity.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():

    # Check to make sure the user is logged in.
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])

    return render_template("index.html")

@app.route("/diary", methods=["GET", "POST"])
@login_required
def diary():
    """Enable user to submit a diary entry."""
    
    # Check for POST
    if request.method == "POST":

        # Define variables
        entry = request.form.get("entry")
        entrytitle = request.form.get("entry-title")
        user_id = session["user_id"]

        # Validate form submission
        if not entrytitle:
            return apology("missing title")
        elif not entry:
            return apology("missing entry")
        elif len(entry) > 500:
            return apology("keep diary entries under 500 characters")

        # Insert into SQL table
        db.execute("INSERT INTO diaryentries (user_id, entry, entrytitle) VALUES(?, ?, ?)", session["user_id"], entry, entrytitle)
        return redirect("/")

    # Check for GET
    else:
        return render_template("diary.html")


@app.route("/entries")
@login_required
def entries():

    # Input diary values into the table
    entrieslog = db.execute(
        "SELECT entrytitle, entry, time FROM diaryentries WHERE user_id = ? ORDER BY time DESC", session["user_id"])
    return render_template("entries.html", entrieslog=entrieslog)

@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():

    """Enable user to submit answers to mental health quiz."""

    # Check for POST
    if request.method == "POST":

        # Get list of emotions submitted via the checkbox
        emotion_list = request.form.getlist('emotions')

        # Convert list to string
        emotion_string = ", ".join(emotion_list)

        # Get value from stress slider
        stressslider = request.form.get('stressslider')

        # Get value from happiness slider
        happinessslider = request.form.get('happinessslider')

        # Insert submission into SQL
        db.execute("INSERT INTO emotions (user_id, emotionlist, stress_slider, happiness_slider) VALUES (?, ?, ?, ?)", session["user_id"], emotion_string, stressslider, happinessslider)

        return render_template("quizzed.html", emotion_string=emotion_string)

    # Check for GET
    else:
        return render_template("quiz.html")

@app.route("/viz")
@login_required
def viz():
    """User can see results of previous mental health quizzes."""

    # Select all information from emotions table
    emotionlog = db.execute(
        "SELECT time, emotionlist, stress_slider, happiness_slider FROM emotions WHERE user_id = ? ORDER BY time DESC", session["user_id"])

    return render_template("viz.html", emotionlog=emotionlog, string_word_count=string_word_count)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation matches password
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation do not match", 400)
        
        # Generate hash for password using given function
        hash_variable = generate_password_hash(request.form.get("password"))
        
        # Account for instances where the username is already taken
        try:
            id = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), hash_variable)
        except ValueError:
            return apology("username taken")

        # Log the user in
        session["user_id"] = id

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/suggest", methods=["GET", "POST"])
@login_required
def suggest():
    return render_template("suggest.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
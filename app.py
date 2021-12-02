import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

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

# Make sure API key is set
# if not os.environ.get("API_KEY"):
    # raise RuntimeError("API_KEY not set")

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
    # Extract all stocks purchased, consolidate number of shares based on symbol
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])

    return render_template("index.html", username=username)

@app.route("/diary", methods=["GET", "POST"])
@login_required
def diary():
    """Enable user to buy a stock."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("entry"):
            return apology("missing entry")
        if  request.form.get("entry"):
            return apology("missing shares")
        elif not request.form.get("shares").isdigit():
            return apology("invalid shares")
        shares = int(request.form.get("shares"))
        if not shares:
            return apology("too few shares")

        # Get stock quote
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology("invalid symbol")

        # Cost to buy
        cost = shares * quote["price"]

        # Get user's cash balance
        rows = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        if not rows:
            return apology("missing user")
        cash = rows[0]["cash"]

        # Ensure user can afford
        if cash < cost:
            return apology("can't afford")

        # Record purchase
        db.execute("""INSERT INTO transactions (user_id, symbol, shares, price)
            VALUES(:user_id, :symbol, :shares, :price)""",
                   user_id=session["user_id"], symbol=quote["symbol"], shares=shares, price=quote["price"])

        # Deduct cash
        db.execute("UPDATE users SET cash = cash - :cost WHERE id = :id",
                   cost=cost, id=session["user_id"])

        # Display portfolio
        flash("Bought!")


    # GET
    else:'''
    return render_template("diary.html")


@app.route("/entries")
@login_required
def entries():
    return redirect("/")


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


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user
    When requested via GET, display registration form
    When form is submitted via POST, check for possible errors and insert new user
    into users table.
    Log user in.
    """
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
    return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
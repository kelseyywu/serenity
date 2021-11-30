import os

# add test

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    """Show portfolio of stocks
    Display HTML table with all stocks owned,
    number of shares of each stock,
    total value of each holding.
    Display user's current cash balance.
    Display total value of stocks and cash together."""

    # Extract all stocks purchased, consolidate number of shares based on symbol
    stocks = db.execute(
        "SELECT symbol, price, SUM(shares) AS num_shares FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])

    # Extract current amount of cash
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    # Set total value to current amount of cash
    total_value = cash

    # Add value of shares from each symbol owned
    for i in stocks:
        total_value += i["price"] * i["num_shares"]

    return render_template("index.html", stocks=stocks, cash=cash, total_value=total_value, usd=usd)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock
    When requested via GET, display form to buy a stock
    When form is submitted via POST, purchase the stock so long as the 
    user can afford it."""
    if request.method == "POST":

        # Ensure user enters a symbol
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        
        # Ensure symbol is valid
        elif not lookup(request.form.get("symbol")):
            return apology("lookup unsuccessful", 400)
        
        # Ensure user enters number of shares
        if not request.form.get("shares"):
            return apology("must provide number of shares", 400)

        # Ensure user enters an integer
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("must enter an integer", 400)

        # Ensure user does try to purchase a negative number or 0 shares
        if shares <= 0:
            return apology("must enter positive number", 400)

        # Extract current amount of cash
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        # Calculate total price of shares that user is trying to buy
        shares_price = shares * lookup(request.form.get("symbol"))["price"]

        # Ensure user has enough cash to afford the shares
        if shares_price > cash:
            return apology("cannot afford number of shares at current price", 403)

        # Subtract price of purchased shares
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", shares_price, session["user_id"])

        # Record this purchase into the transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)", 
        session["user_id"], request.form.get("symbol"), shares, lookup(request.form.get("symbol"))["price"])

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions
    Display a table with a history of all transactions, listing one row for every buy
    and every sell. Include what stock, how many shares, when transaction happened."""

    # Extract past transactions data from database
    transactions = db.execute(
        "SELECT symbol, shares, time FROM transactions WHERE user_id = ? ORDER BY time DESC", session["user_id"])

    return render_template("history.html", transactions=transactions)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote.
    When requested via GET, display form to request a stock quote.
    When form is submitted via POST, lookup the stock symbol by calling
    the lookup function, and display the results.
    """
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure the symbol is valid
        if not lookup(request.form.get("symbol")):
            return apology("lookup unsuccessful", 400)

        return render_template("quoted.html", symbol=lookup(request.form.get("symbol")), usd=usd)

    else:
        return render_template("quote.html")


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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock
    When requested via GET, display form to sell a stock.
    When form is submitted via POST, check for errors and sell the specified
    number of shares of stock and update the user's cash."""

    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        # Ensure number of shares was submitted
        if not request.form.get("shares"):
            return apology("must provide number of shares", 403)

        shares_sold = int(request.form.get("shares"))

        # Ensure number of shares entered is positive
        if shares_sold <= 0:
            return apology("must enter positive number", 403)

        # Ensure number of shares entered is an integer
        if not shares_sold:
            return apology("shares must be integer", 403)

        # Find existing number of shares under that symbol
        existing_shares = db.execute("SELECT shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", 
        session["user_id"], request.form.get("symbol"))[0]["shares"]

        # If user does not own that many shares of the stock, return apology message
        if shares_sold > existing_shares:
            return apology("you do not have enough shares", 400)

        # Calculate amount received when symbol is sold
        selling_price = shares_sold * lookup(request.form.get("symbol"))["price"]

        # Update users' cash to indicate amount received when symbol is sold
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", selling_price, session["user_id"])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)", 
        session["user_id"], request.form.get("symbol"), -shares_sold, lookup(request.form.get("symbol"))["price"])

        return redirect("/")

    else:
        past_symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])
        return render_template("sell.html", past_symbols=past_symbols)


@app.route("/addcash", methods=["GET", "POST"])
@login_required
def addcash():
    """Allow user to add additional cash to their account."""

    if request.method == "POST":

        # Ensure additional cash amount was submitted
        if not request.form.get("addcash"):
            return apology("must provide added cash amount", 403)

        # Update cash amount
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", request.form.get("addcash"), session["user_id"])

        return redirect("/")

    else:
        return render_template("addcash.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
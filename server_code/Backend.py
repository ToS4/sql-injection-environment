import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.files
from anvil.files import data_files
import anvil.server
import sqlite3
import requests

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
def login(username, passwort):
  connection = sqlite3.connect(data_files["database.db"])
  cursor = connection.cursor()

  # Vulnerable SQL query
  query = f"SELECT Username, IsAdmin FROM Users WHERE Username = '{username}' AND Password = '{passwort}'"
  try:
    cursor.execute(query)
  except Exception as e:
    return 0, f"Login failed! {query} {e}"

  user = cursor.fetchone()
  accountNo = None
  anvil.server.session["redirected"] = False
  if user and username == user[0]:
    accountNo = cursor.execute(f"SELECT AccountNo FROM Users WHERE Username = '{username}'").fetchone()
  if user and username == user[0] and user[1] == 1:
    query = f"SELECT Password FROM Users WHERE Username = '{username}' AND Password = '{passwort}'"
    pw = cursor.execute(query).fetchone()
    if pw and passwort == pw[0]:
      connection.close()
      return 2, "Congratulations you finished the task!"
  if user:
    anvil.server.session['redirected'] = True
    connection.close()
    return 1, accountNo
  else:
    connection.close()
    return 0, f"Login failed! {query}"

@anvil.server.route("/users")
def login_with_accountNumber(**params):
  connection = sqlite3.connect(data_files["database.db"])
  cursor = connection.cursor()
  
  if "redirected" in anvil.server.session:
    redirected = anvil.server.session["redirected"]
    if not redirected:
      return False, "Not Logged in!"
  else:
    return False, "Not Logged in!"

  AccountNo = params['AccountNo']
  
  if AccountNo:
    # Query the balance and user details based on AccountNo
    query_balance = f"SELECT Balance FROM Balances WHERE AccountNo = {AccountNo}"
    query_user = f"SELECT Username FROM Users WHERE AccountNo = {AccountNo}"
    try:
      balance = cursor.execute(query_balance).fetchall()
      user = cursor.execute(query_user).fetchall()
    except Exception as e:
      return f"User not found.{query_user} {query_balance} {e}"

    user = [u[0] for u in user if isinstance(u, tuple)]
    balance = [b[0] for b in balance if isinstance(b, tuple)]
    user = user[0] if len(user) == 1 else user
    balance = balance[0] if len(balance) == 1 else balance
    # formatting end
    if user:
      return f"Welcome {user}! Your balance is {balance}."
    else:
      return f"User not found. {query_user} {query_balance}"

  return "Login successful but 'AccountNo' was not passed."
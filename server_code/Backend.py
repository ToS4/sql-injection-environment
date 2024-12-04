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
def get_level():
  if "level" in anvil.server.session:
    return anvil.server.session["level"]
  return 1

@anvil.server.callable
def get_server_msg():
  if "server_msg" in anvil.server.session:
    return anvil.server.session["server_msg"]
  

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
  anvil.server.session['level'] = 1
  if user and username == user[0]:
    accountNo = cursor.execute(f"SELECT AccountNo FROM Users WHERE Username = '{username}'").fetchone()
  if user and username == user[0] and user[1] == 1:
    query = f"SELECT Password FROM Users WHERE Username = '{username}' AND Password = '{passwort}'"
    pw = cursor.execute(query).fetchone()
    if pw and passwort == pw[0]:
      connection.close()
      return 2, "Congratulations you finished the task!"
  if user:
    anvil.server.session['level'] = 2
    msg = "Login successful but 'AccountNo' was not passed. (1)"
    anvil.server.session["server_msg"] = msg
    connection.close()
    return 1, accountNo
  else:
    connection.close()
    return 0, f"Login failed! {query}"

@anvil.server.route("/")
def login_with_accountNumber(**params):
  connection = sqlite3.connect(data_files["database.db"])
  cursor = connection.cursor()

  level = get_level()
  
  if not level or level == 1:
    msg = "Not Logged in!"
    anvil.server.session["server_msg"] = msg
    return msg

  AccountNo = params.get('AccountNo')
  
  if AccountNo:
    query_balance = f"SELECT Balance FROM Balances WHERE AccountNo = {AccountNo}"
    query_user = f"SELECT Username FROM Users WHERE AccountNo = {AccountNo}"

    try:
      balance = cursor.execute(query_balance).fetchall()
      user = cursor.execute(query_user).fetchall()
    except Exception as e:
      msg = f"User not found.{query_user} {query_balance} {e}"
      anvil.server.session["server_msg"] = msg
      return msg

    user = [u[0] for u in user if isinstance(u, tuple)]
    balance = [b[0] for b in balance if isinstance(b, tuple)]
    user = user[0] if len(user) == 1 else user
    balance = balance[0] if len(balance) == 1 else balance

    if user:
      msg = f"Welcome {user}! Your balance is {balance}."
      anvil.server.session["server_msg"] = msg
      return msg
    else:
      msg = f"User not found. {query_user} {query_balance}"
      anvil.server.session["server_msg"] = msg
      return msg

  msg = "Login successful but 'AccountNo' was not passed. (2)"
  anvil.server.session["server_msg"] = msg
  return msg